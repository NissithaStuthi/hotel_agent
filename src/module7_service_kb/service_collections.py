"""Module 7: Separate Service Knowledge Collections & Retrieval Accuracy Benchmarking

Creates and maintains dedicated ChromaDB vector collections for each of the 9 hotel services:
- Housekeeping
- Laundry
- Room Service
- Wi-Fi
- Parking
- Gym
- Pool
- Spa
- Restaurants

Evaluates retrieval precision, accuracy, and collection-level separation.
"""

import json
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
import chromadb

from src.config import CHROMA_PERSIST_DIR
from src.module7_service_kb.models import ServiceCategory


class ServiceCollectionManager:
    """Manages isolated ChromaDB collections for each hotel service domain."""

    CORE_SERVICES = [
        ServiceCategory.HOUSEKEEPING,
        ServiceCategory.LAUNDRY,
        ServiceCategory.ROOM_SERVICE,
        ServiceCategory.WIFI,
        ServiceCategory.PARKING,
        ServiceCategory.GYM,
        ServiceCategory.POOL,
        ServiceCategory.SPA,
        ServiceCategory.RESTAURANTS,
    ]

    def __init__(
        self,
        persist_dir: Path = CHROMA_PERSIST_DIR,
        data_path: Optional[Path] = None
    ):
        self.persist_dir = persist_dir
        self.data_path = data_path or (Path("data") / "hotel_services.json")
        self.client = chromadb.PersistentClient(path=str(self.persist_dir))
        self.collections: Dict[ServiceCategory, chromadb.Collection] = {}
        self.raw_data: Dict[str, Any] = {}
        
        self._load_data()
        self._init_collections()

    def _load_data(self) -> None:
        """Loads structured hotel services JSON."""
        if self.data_path.exists():
            with open(self.data_path, "r", encoding="utf-8") as f:
                self.raw_data = json.load(f)
        else:
            self.raw_data = {}

    def _get_collection_name(self, category: ServiceCategory) -> str:
        return f"service_{category.value}"

    def _init_collections(self) -> None:
        """Initializes separate vector collections for all 9 core services."""
        for cat in self.CORE_SERVICES:
            col_name = self._get_collection_name(cat)
            collection = self.client.get_or_create_collection(
                name=col_name,
                metadata={"hnsw:space": "cosine", "service": cat.value}
            )
            self.collections[cat] = collection
            
            # Populate if empty
            if collection.count() == 0:
                self._populate_collection(cat, collection)

    def _populate_collection(self, category: ServiceCategory, collection: chromadb.Collection) -> None:
        """Chunks and indexes service content into its specific collection."""
        cat_key = category.value
        service_data = self.raw_data.get(cat_key, {})
        if not service_data:
            return

        documents: List[str] = []
        metadatas: List[Dict[str, Any]] = []
        ids: List[str] = []

        service_name = service_data.get("name", category.value.title())
        description = service_data.get("description", "")
        contact = service_data.get("contact", "")

        # 1. Overview Chunk
        overview_text = f"Service: {service_name}\nDescription: {description}\nContact: {contact}"
        documents.append(overview_text)
        metadatas.append({"service": category.value, "type": "overview", "title": service_name})
        ids.append(f"{category.value}_overview")

        # 2. Schedule & Hours Chunk
        schedule = service_data.get("schedule") or service_data.get("hours", {})
        if schedule:
            sched_str = "\n".join(f"{k.capitalize()}: {v}" for k, v in schedule.items() if isinstance(v, str))
            documents.append(f"{service_name} Operating Hours & Availability:\n{sched_str}")
            metadatas.append({"service": category.value, "type": "hours", "title": f"{service_name} Hours"})
            ids.append(f"{category.value}_hours")

        # 3. Pricing Chunk
        pricing = service_data.get("pricing", {})
        if pricing:
            price_text = f"{service_name} Pricing:\nBase Price: ${pricing.get('base_price', 0.0)} {pricing.get('unit', '')}\n"
            if pricing.get("tiers"):
                price_text += "Tiers: " + ", ".join(f"{k}: ${v}" for k, v in pricing["tiers"].items()) + "\n"
            if pricing.get("complimentary_for"):
                price_text += "Complimentary for: " + ", ".join(pricing["complimentary_for"]) + "\n"
            documents.append(price_text)
            metadatas.append({"service": category.value, "type": "pricing", "title": f"{service_name} Pricing"})
            ids.append(f"{category.value}_pricing")

        # 4. Service Specifics Chunks
        if category == ServiceCategory.HOUSEKEEPING:
            items = service_data.get("requestable_items", [])
            turnaround = service_data.get("turnaround_times", {})
            services = service_data.get("services", [])
            hk_text = f"Housekeeping Requestable Items:\n" + "\n".join(f"- {i}" for i in items)
            hk_text += "\nTurnaround Times:\n" + "\n".join(f"- {k}: {v}" for k, v in turnaround.items())
            hk_text += "\nServices Offered:\n" + "\n".join(f"- {s}" for s in services)
            documents.append(hk_text)
            metadatas.append({"service": category.value, "type": "items_turnaround", "title": "Housekeeping Items & Turnaround"})
            ids.append("hk_items_turnaround")

        elif category == ServiceCategory.LAUNDRY:
            item_prices = service_data.get("item_pricing", {})
            std_time = service_data.get("turnaround_standard", "")
            exp_time = service_data.get("turnaround_express", "")
            lnd_text = f"Laundry Item Pricing:\n" + "\n".join(f"- {k.replace('_', ' ').title()}: ${v:.2f}" for k, v in item_prices.items())
            lnd_text += f"\nTurnaround Standard: {std_time}\nTurnaround Express: {exp_time} (50% surcharge)"
            documents.append(lnd_text)
            metadatas.append({"service": category.value, "type": "garment_pricing", "title": "Laundry Garment Pricing & Turnaround"})
            ids.append("laundry_garment_pricing")

        elif category == ServiceCategory.ROOM_SERVICE:
            menu = service_data.get("menu_categories", {})
            for section, items in menu.items():
                items_text = f"Room Service {section.replace('_', ' ').title()} Menu:\n"
                for item in items:
                    items_text += f"- {item['name']} (${item['price']:.2f}, {item.get('dietary', '')}): {item.get('desc', '')}\n"
                items_text += f"Delivery Time: {service_data.get('delivery_time', '30-45 mins')}\n"
                documents.append(items_text)
                metadatas.append({"service": category.value, "type": f"menu_{section}", "title": f"Room Service {section.title()} Menu"})
                ids.append(f"rs_menu_{section}")

        elif category == ServiceCategory.WIFI:
            networks = service_data.get("networks", [])
            wifi_text = "Hotel Wi-Fi Networks & Access Credentials:\n"
            for net in networks:
                wifi_text += f"- SSID: {net['ssid']} | Speed: {net['speed']} | Cost: {net['cost']} | Login: {net['login']} | Best for: {net['best_for']}\n"
            wifi_text += f"Device Limit: {service_data.get('device_limit', 5)} devices per guest room.\nSupport: {service_data.get('support_contact', '')}"
            documents.append(wifi_text)
            metadatas.append({"service": category.value, "type": "networks", "title": "Wi-Fi Networks & Passcodes"})
            ids.append("wifi_networks")

        elif category == ServiceCategory.PARKING:
            options = service_data.get("options", [])
            pkg_text = "Parking & Valet Options:\n"
            for opt in options:
                pkg_text += f"- {opt['type']}: {opt['rate']} ({opt.get('privileges', '')})\n"
            pkg_text += f"EV Supercharging: Level 2 and Tesla chargers complimentary for registered guests.\n"
            documents.append(pkg_text)
            metadatas.append({"service": category.value, "type": "options", "title": "Parking Rates & EV Charging"})
            ids.append("parking_options")

        elif category == ServiceCategory.GYM:
            equip = service_data.get("equipment", [])
            classes = service_data.get("classes", [])
            gym_text = "Fitness Pavilion Equipment & Amenities:\n" + "\n".join(f"- {e}" for e in equip)
            gym_text += "\nGroup Classes & Personal Training:\n"
            for c in classes:
                gym_text += f"- {c['name']} ({c['schedule']}): {c['cost']}\n"
            gym_text += f"Age Requirement: {service_data.get('age_restriction', 16)}+ years old."
            documents.append(gym_text)
            metadatas.append({"service": category.value, "type": "classes_equipment", "title": "Gym Equipment & Classes"})
            ids.append("gym_classes_equipment")

        elif category == ServiceCategory.POOL:
            pools = service_data.get("pools", [])
            pool_text = "Resort Pools & Aquatic Features:\n"
            for p in pools:
                pool_text += f"- {p['name']}: {p['type']} (Hours: {p['hours']}). {p.get('amenities', '')}\n"
            pool_text += f"Cabana Rentals: $150 half-day / $250 full-day.\nLifeguard: {service_data.get('lifeguard_hours', '9am-7pm')}."
            documents.append(pool_text)
            metadatas.append({"service": category.value, "type": "pools_detail", "title": "Resort Pools & Cabanas"})
            ids.append("pool_details")

        elif category == ServiceCategory.SPA:
            treatments = service_data.get("signature_treatments", [])
            spa_text = "The Azure Wellness Spa Signature Treatments:\n"
            for t in treatments:
                spa_text += f"- {t['name']} ({t['duration']}, ${t['price']:.2f}): {t.get('desc', '')}\n"
            documents.append(spa_text)
            metadatas.append({"service": category.value, "type": "treatments", "title": "Spa Signature Treatments"})
            ids.append("spa_treatments")

        elif category == ServiceCategory.RESTAURANTS:
            venues = service_data.get("venues", [])
            rest_text = "Resort Restaurants & Dining Venues:\n"
            for v in venues:
                rest_text += f"- {v['name']} ({v['cuisine']}, {v['style']}): Hours {v['hours']}. Dress Code: {v['dress_code']}. Signature: {v.get('signature', '')}\n"
            documents.append(rest_text)
            metadatas.append({"service": category.value, "type": "venues", "title": "Resort Restaurants Collection"})
            ids.append("restaurant_venues")

        # 5. Policies Chunk
        policies = service_data.get("policies", [])
        if policies:
            pol_text = f"{service_name} Regulations & Policies:\n" + "\n".join(f"- {p}" for p in policies)
            documents.append(pol_text)
            metadatas.append({"service": category.value, "type": "policies", "title": f"{service_name} Policies"})
            ids.append(f"{category.value}_policies")

        # Upsert
        collection.upsert(ids=ids, documents=documents, metadatas=metadatas)

    def retrieve_from_service(
        self,
        category: ServiceCategory,
        query: str,
        top_k: int = 3
    ) -> List[Dict[str, Any]]:
        """Retrieves knowledge chunks strictly from the requested service collection."""
        if category not in self.collections:
            return []

        collection = self.collections[category]
        results = collection.query(query_texts=[query], n_results=min(top_k, max(1, collection.count())))
        
        chunks = []
        if results and results["documents"]:
            docs = results["documents"][0]
            metas = results["metadatas"][0] if results.get("metadatas") else [{}] * len(docs)
            dists = results["distances"][0] if results.get("distances") else [0.0] * len(docs)
            ids = results["ids"][0] if results.get("ids") else [""] * len(docs)

            for doc, meta, dist, chunk_id in zip(docs, metas, dists, ids):
                similarity = 1.0 - (dist / 2.0) if dist is not None else 0.8
                chunks.append({
                    "chunk_id": chunk_id,
                    "content": doc,
                    "metadata": meta,
                    "similarity": similarity,
                    "service": category.value
                })
        return chunks

    def route_query_to_service(self, query: str) -> ServiceCategory:
        """Determines the most relevant service category for a query."""
        q = query.lower()
        
        # Keyword heuristic routing first
        if any(w in q for w in ["towel", "pillow", "blanket", "housekeeping", "cleaning", "crib", "toiletry", "shampoo", "dyson"]):
            return ServiceCategory.HOUSEKEEPING
        if any(w in q for w in ["laundry", "dry clean", "press", "ironing", "wash", "garment", "suit pressing", "shirt"]):
            return ServiceCategory.LAUNDRY
        if any(w in q for w in ["room service", "in-room dining", "burger", "pizza", "breakfast in bed", "midnight snack", "menu"]):
            return ServiceCategory.ROOM_SERVICE
        if any(w in q for w in ["wifi", "wi-fi", "internet", "network", "password", "ssid", "connect", "mbps"]):
            return ServiceCategory.WIFI
        if any(w in q for w in ["park", "valet", "car", "ev charging", "tesla", "garage", "vehicle"]):
            return ServiceCategory.PARKING
        if any(w in q for w in ["gym", "workout", "fitness", "treadmill", "peloton", "weights", "yoga class", "personal trainer"]):
            return ServiceCategory.GYM
        if any(w in q for w in ["pool", "swimming", "cabana", "sun lounger", "splash", "infinity pool", "lifeguard"]):
            return ServiceCategory.POOL
        if any(w in q for w in ["spa", "massage", "facial", "hydrotherapy", "thalassotherapy", "sauna", "wellness treatment"]):
            return ServiceCategory.SPA
        if any(w in q for w in ["restaurant", "dinner", "lunch", "seafood grill", "bistro", "dress code", "table reservation", "bar", "cocktail"]):
            return ServiceCategory.RESTAURANTS

        # Fallback: Vector similarity score across all 9 collections
        best_category = ServiceCategory.HOUSEKEEPING
        best_similarity = -1.0
        for cat in self.CORE_SERVICES:
            chunks = self.retrieve_from_service(cat, query, top_k=1)
            if chunks and chunks[0]["similarity"] > best_similarity:
                best_similarity = chunks[0]["similarity"]
                best_category = cat
        return best_category

    def evaluate_retrieval_accuracy(
        self,
        test_suite: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """Evaluates retrieval accuracy across all 9 separate service collections."""
        if test_suite is None:
            test_suite = [
                # Housekeeping
                {"query": "Can I get extra plush towels and a memory foam pillow sent to my room?", "target": ServiceCategory.HOUSEKEEPING, "expected_keywords": ["towel", "pillow"]},
                {"query": "What are the hours for daily morning housekeeping and evening turndown?", "target": ServiceCategory.HOUSEKEEPING, "expected_keywords": ["turndown", "8:30"]},
                # Laundry
                {"query": "How much does it cost to dry clean a 2-piece suit and press a silk blouse?", "target": ServiceCategory.LAUNDRY, "expected_keywords": ["suit", "35"]},
                {"query": "Is 4-hour express laundry service available if I need it today?", "target": ServiceCategory.LAUNDRY, "expected_keywords": ["express", "4 hours"]},
                # Room Service
                {"query": "What time is breakfast served in-room, and do you have wagyu burgers on the overnight menu?", "target": ServiceCategory.ROOM_SERVICE, "expected_keywords": ["wagyu", "breakfast"]},
                {"query": "Is in-room dining available 24 hours with vegetarian options?", "target": ServiceCategory.ROOM_SERVICE, "expected_keywords": ["24/7", "vegetarian"]},
                # Wi-Fi
                {"query": "What is the Wi-Fi network name and how many devices can I connect?", "target": ServiceCategory.WIFI, "expected_keywords": ["grandazure_guest", "device"]},
                {"query": "Do you offer ultra-fast 300 Mbps internet for business video conferences?", "target": ServiceCategory.WIFI, "expected_keywords": ["300 mbps", "ultra"]},
                # Parking
                {"query": "How much is overnight valet parking and where are the Tesla EV superchargers located?", "target": ServiceCategory.PARKING, "expected_keywords": ["45", "tesla"]},
                {"query": "Is self-parking complimentary or is there a daily garage fee?", "target": ServiceCategory.PARKING, "expected_keywords": ["25", "self-parking"]},
                # Gym
                {"query": "Is the fitness pavilion open 24 hours and do you have Peloton bikes?", "target": ServiceCategory.GYM, "expected_keywords": ["24/7", "peloton"]},
                {"query": "What time is the complimentary sunrise oceanfront yoga class?", "target": ServiceCategory.GYM, "expected_keywords": ["7:30 am", "yoga"]},
                # Pool
                {"query": "What is the water temperature of the cliffside infinity pool and what are the hours?", "target": ServiceCategory.POOL, "expected_keywords": ["82°f", "6:00 am"]},
                {"query": "Is there an adults-only serenity pool with private cabana rentals?", "target": ServiceCategory.POOL, "expected_keywords": ["serenity", "150"]},
                # Spa
                {"query": "What signature massages do you offer at The Azure Wellness Spa and what is the advance booking policy?", "target": ServiceCategory.SPA, "expected_keywords": ["mineral", "280"]},
                {"query": "Is the thalassotherapy vitality thermal circuit complimentary with a 60-minute facial?", "target": ServiceCategory.SPA, "expected_keywords": ["thalassotherapy", "complimentary"]},
                # Restaurants
                {"query": "What is the dress code and hours for dinner at Azure Breeze Seafood Grill?", "target": ServiceCategory.RESTAURANTS, "expected_keywords": ["smart casual", "5:30 pm"]},
                {"query": "Do any of the resort restaurants offer French cuisine with Sunday Brunch?", "target": ServiceCategory.RESTAURANTS, "expected_keywords": ["le jardin", "brunch"]}
            ]

        results_by_service: Dict[str, Dict[str, Any]] = {
            cat.value: {"total": 0, "correct_routing": 0, "top1_match": 0, "top3_match": 0}
            for cat in self.CORE_SERVICES
        }
        detailed_evaluations: List[Dict[str, Any]] = []

        for item in test_suite:
            query = item["query"]
            target_cat = item["target"]
            keywords = [k.lower() for k in item["expected_keywords"]]

            # 1. Routing test
            predicted_cat = self.route_query_to_service(query)
            routing_correct = (predicted_cat == target_cat)

            # 2. Retrieval test within the target collection
            retrieved = self.retrieve_from_service(target_cat, query, top_k=3)
            
            top1_hit = False
            top3_hit = False

            if retrieved:
                top1_content = retrieved[0]["content"].lower()
                top1_hit = any(kw in top1_content for kw in keywords)

                all_content = " ".join(r["content"].lower() for r in retrieved)
                top3_hit = any(kw in all_content for kw in keywords)

            stats = results_by_service[target_cat.value]
            stats["total"] += 1
            if routing_correct:
                stats["correct_routing"] += 1
            if top1_hit:
                stats["top1_match"] += 1
            if top3_hit:
                stats["top3_match"] += 1

            detailed_evaluations.append({
                "query": query,
                "target_service": target_cat.value,
                "predicted_service": predicted_cat.value,
                "routing_correct": routing_correct,
                "top1_hit": top1_hit,
                "top3_hit": top3_hit,
                "top_chunk_title": retrieved[0]["metadata"].get("title", "") if retrieved else ""
            })

        total_queries = len(test_suite)
        overall_routing_acc = sum(s["correct_routing"] for s in results_by_service.values()) / total_queries if total_queries else 0.0
        overall_top1_acc = sum(s["top1_match"] for s in results_by_service.values()) / total_queries if total_queries else 0.0
        overall_top3_acc = sum(s["top3_match"] for s in results_by_service.values()) / total_queries if total_queries else 0.0

        return {
            "total_queries_tested": total_queries,
            "overall_routing_accuracy": overall_routing_acc,
            "overall_top1_precision": overall_top1_acc,
            "overall_top3_precision": overall_top3_acc,
            "service_breakdown": results_by_service,
            "detailed_evaluations": detailed_evaluations
        }
