import asyncio

class ToolCoordinator:
    """Agent Skill: 多工具协调与协同工作能力"""
    
    def __init__(self, tools):
        self.tools = tools
        
    def coordinate_tools(self, travel_framework, deep_needs):
        """协调多个工具收集和处理信息"""
        print("【工具协调引擎启动】")
        
        # 收集阶段结果
        collected_data = {
            "transportation": {},
            "accommodation": {},
            "attractions": {},
            "weather": {},
            "budget": {}
        }
        
        # 阶段1：并行数据收集
        collection_results = self._parallel_data_collection(travel_framework)
        collected_data.update(collection_results)
        
        # 阶段2：数据质量评估与补全
        quality_report = self._assess_data_quality(collected_data)
        if quality_report["needs_completion"]:
            collected_data = self._complete_missing_data(collected_data, quality_report)
        
        # 阶段3：基于约束的过滤
        filtered_data = self._apply_constraints_filters(collected_data, deep_needs)
        
        # 阶段4：跨工具数据关联
        integrated_data = self._integrate_cross_tool_data(filtered_data)
        
        # 阶段5：生成洞察和建议
        insights = self._generate_insights(integrated_data, travel_framework, deep_needs)
        
        return {
            "raw_data": collected_data,
            "filtered_data": filtered_data,
            "integrated_data": integrated_data,
            "insights": insights,
            "quality_report": quality_report
        }
    
    def _parallel_data_collection(self, framework):
        """并行调用多个工具收集数据"""
        print("  阶段1: 并行数据收集...")
        
        # 定义异步执行函数
        async def _async_data_collection():
            collection_tasks = []
            
            # 为每个目的地并行收集信息
            for destination in framework["destinations"]:
                # 并行收集任务
                tasks_for_destination = [
                    self._collect_transportation_info(destination),
                    self._collect_accommodation_info(destination, framework),
                    self._collect_attraction_info(destination, framework["theme"]),
                    self._collect_weather_info(destination)
                ]
                collection_tasks.extend(tasks_for_destination)
            
            # 使用 asyncio.gather 并行执行所有收集任务
            task_results = await asyncio.gather(*collection_tasks)
            
            results = {}
            # 处理任务结果
            for result in task_results:
                category, destination, data =  result
                if destination not in results:
                    results[destination] = {}
                results[destination][category] = data
            
            # 并行收集预算信息
            budget_data = await self._collect_budget_info(framework)
            results["budget"] = budget_data
            
            return results
        
        # 运行异步收集函数
        return asyncio.run(_async_data_collection())
    
    async def _collect_transportation_info(self, destination):
        """收集交通信息（协调多个交通相关工具）"""
        print(f"    → 为{destination}收集交通信息")
        
        # 协调多个工具：航班查询 + 火车查询 + 当地交通
        flights = self.tools["search_flights"](departure_city="北京", arrival_city="昆明")
        trains = self._query_train_schedule("昆明", destination)
        local_transport = self._query_local_transport(destination)
        
        return ("transportation", destination, {
            "flights": flights[:2],  # 取前2个选项
            "trains": trains,
            "local_transport": local_transport,
            "recommendation": self._recommend_transport_option(flights, trains, local_transport)
        })
    
    def _query_train_schedule(self, from_city, to_city):
        """查询火车班次（模拟工具）"""
        # 实际会调用火车票API
        train_schedules = {
            "昆明-大理": [
                {"train": "D8672", "departure": "08:00", "arrival": "10:30", "duration": "2.5h", "price": 145},
                {"train": "D8676", "departure": "14:00", "arrival": "16:35", "duration": "2.5h", "price": 145}
            ],
            "大理-丽江": [
                {"train": "D8137", "departure": "09:00", "arrival": "10:30", "duration": "1.5h", "price": 52}
            ]
        }
        
        key = f"{from_city}-{to_city}"
        return train_schedules.get(key, [])
    
    def _query_local_transport(self, destination):
        """查询当地交通（模拟工具）"""
        local_transport = {
            "大理": [
                {"type": "包车", "description": "古城周边一日游", "price": "300-500元/天"},
                {"type": "电动车", "description": "洱海骑行", "price": "50-80元/天"},
                {"type": "出租车", "description": "市内交通", "price": "起步价8元"}
            ],
            "沙溪古镇": [
                {"type": "步行", "description": "古镇内可步行游览", "price": "免费"},
                {"type": "马车", "description": "当地特色交通", "price": "20-50元/次"}
            ]
        }
        return local_transport.get(destination, [])
    
    def _recommend_transport_option(self, flights, trains, local_transport):
        """基于多源信息推荐交通方案"""
        # 智能推荐逻辑
        recommendations = []
        
        if flights and len(flights) > 0:
            best_flight = min(flights, key=lambda x: x.get("price", float('inf')))
            recommendations.append({
                "type": "航班",
                "recommendation": f"选择{best_flight['airline']} {best_flight['flight_no']}",
                "reason": f"价格最优({best_flight['price']}元)，时间合适({best_flight['departure_time']})"
            })
        
        if trains and len(trains) > 0:
            best_train = trains[0]  # 取第一班
            recommendations.append({
                "type": "火车",
                "recommendation": f"高铁{best_train['train']}次",
                "reason": f"准时便捷，{best_train['duration']}到达"
            })
        
        if local_transport:
            # 根据类型推荐
            for transport in local_transport:
                if transport["type"] == "包车":
                    recommendations.append({
                        "type": "当地交通",
                        "recommendation": "建议包车",
                        "reason": "灵活自由，适合家庭或小团体"
                    })
                    break
        
        return recommendations
    
    async def _collect_accommodation_info(self, destination, framework):
        """收集住宿信息（智能筛选）"""
        print(f"    → 为{destination}收集住宿信息")
        
        # 基于框架主题和用户偏好动态生成搜索参数
        search_params = self._generate_hotel_search_params(destination, framework)
        
        # 调用酒店搜索工具
        hotels = self.tools["search_hotels_tool"](
            city=destination,
            check_in_date="2024-06-01",
            check_out_date="2024-06-08",
            budget_per_night=search_params["budget_per_night"],
            keywords=search_params["keywords"]
        )
        
        # 智能排序和筛选
        sorted_hotels = self._rank_hotels(hotels, framework["theme"], search_params["preferences"])
        
        return ("accommodation", destination, {
            "hotels": sorted_hotels[:5],  # 返回前5个推荐
            "search_params": search_params,
            "recommendation_strategy": self._get_accommodation_strategy(framework["theme"])
        })
    
    def _generate_hotel_search_params(self, destination, framework):
        """基于框架生成酒店搜索参数"""
        # 根据主题调整预算
        theme = framework["theme"]["primary_theme"]
        base_budget = 300
        
        if theme == "休闲度假":
            budget_multiplier = 1.5
            keywords = ["度假", "舒适", "景观"]
        elif theme == "民族文化深度体验":
            budget_multiplier = 1.0
            keywords = ["特色", "民宿", "文化"]
        else:  # 自然风光探索等
            budget_multiplier = 0.8
            keywords = ["经济", "干净", "方便"]
        
        # 根据目的地商业化程度调整
        dest_info = framework["destinations"].get(destination, {})
        if dest_info.get("commercial_level") == "低":
            keywords.append("安静")
            budget_multiplier *= 0.9  # 非商业化地区价格较低
        
        return {
            "budget_per_night": int(base_budget * budget_multiplier),
            "keywords": keywords,
            "preferences": {
                "culture_emphasis": theme == "民族文化深度体验",
                "quiet_preferred": "安静" in keywords,
                "budget_conscious": framework["total_budget"] < 10000
            }
        }
    
    def _rank_hotels(self, hotels, theme, preferences):
        """基于多维度对酒店进行智能排序"""
        if not hotels:
            return []
        
        scored_hotels = []
        for hotel in hotels:
            score = 0
            
            # 评分权重（0-5分）
            if hotel.get("rating"):
                score += hotel["rating"] * 20  # 评分占20%
            
            # 价格分（越便宜分越高）
            price = hotel.get("price_per_night", 0)
            if price > 0:
                price_score = max(0, 100 - price)  # 简单线性模型
                score += price_score * 0.3  # 价格占30%
            
            # 主题匹配分
            features = hotel.get("features", [])
            theme_keywords = {
                "民族文化深度体验": ["特色", "民宿", "文化", "传统"],
                "自然风光探索": ["景观", "山景", "湖景", "自然"],
                "休闲度假": ["舒适", "度假", "豪华", "设施"]
            }
            
            if theme["primary_theme"] in theme_keywords:
                for keyword in theme_keywords[theme["primary_theme"]]:
                    if any(keyword in feature for feature in features):
                        score += 30  # 主题匹配加30分
            
            # 用户偏好匹配
            if preferences.get("quiet_preferred") and any("安静" in feature for feature in features):
                score += 25
            
            hotel["recommendation_score"] = score
            scored_hotels.append(hotel)
        
        # 按分数降序排序
        scored_hotels.sort(key=lambda x: x["recommendation_score"], reverse=True)
        
        return scored_hotels
    
    def _get_accommodation_strategy(self, theme):
        """获取住宿策略"""
        strategies = {
            "民族文化深度体验": "优先选择有文化特色的民宿，位置靠近文化景点",
            "自然风光探索": "选择景观好的住宿，便于早晚拍摄",
            "休闲度假": "重视住宿舒适度和设施，位置便利",
            "经典观光": "选择交通便利的酒店，便于每日出行"
        }
        return strategies.get(theme["primary_theme"], "平衡性价比和位置")
    
    async def _collect_attraction_info(self, destination, theme):
        """收集景点信息（智能过滤）"""
        print(f"    → 为{destination}收集景点信息")
        
        # 获取所有景点
        all_attractions = self._get_destination_attractions(destination)
        
        # 基于主题过滤
        filtered_attractions = self._filter_attractions_by_theme(all_attractions, theme)
        
        # 排序和分组
        organized_attractions = self._organize_attractions(filtered_attractions, theme)
        
        return ("attractions", destination, organized_attractions)
    
    def _get_destination_attractions(self, destination):
        """获取目的地所有景点（模拟）"""
        attractions_db = {
            "大理": [
                {"name": "大理古城", "type": "文化", "commercial_level": "中等", "time_needed": "半天"},
                {"name": "洱海", "type": "自然", "commercial_level": "低", "time_needed": "全天"},
                {"name": "崇圣寺三塔", "type": "文化", "commercial_level": "中等", "time_needed": "2-3小时"},
                {"name": "喜洲古镇", "type": "文化", "commercial_level": "低", "time_needed": "半天"}
            ],
            "沙溪古镇": [
                {"name": "沙溪古镇", "type": "文化", "commercial_level": "低", "time_needed": "全天"},
                {"name": "石宝山", "type": "自然", "commercial_level": "低", "time_needed": "半天"},
                {"name": "茶马古道", "type": "文化", "commercial_level": "低", "time_needed": "2-3小时"}
            ],
            "丽江": [
                {"name": "丽江古城", "type": "文化", "commercial_level": "高", "time_needed": "全天"},
                {"name": "玉龙雪山", "type": "自然", "commercial_level": "高", "time_needed": "全天"},
                {"name": "束河古镇", "type": "文化", "commercial_level": "中等", "time_needed": "半天"}
            ]
        }
        return attractions_db.get(destination, [])
    
    def _filter_attractions_by_theme(self, attractions, theme):
        """基于主题过滤景点"""
        theme_filters = {
            "民族文化深度体验": ["文化", "历史", "民俗"],
            "自然风光探索": ["自然", "景观", "户外"],
            "休闲度假": ["休闲", "轻松", "体验"],
            "经典观光": ["标志性", "必去"]
        }
        
        primary_theme = theme["primary_theme"]
        filter_keywords = theme_filters.get(primary_theme, [])
        
        if not filter_keywords:
            return attractions
        
        filtered = []
        for attr in attractions:
            attr_type = attr.get("type", "")
            attr_name = attr.get("name", "")
            
            # 检查是否匹配主题关键词
            matches_theme = any(keyword in attr_type for keyword in filter_keywords)
            
            # 对于民族文化主题，特别考虑商业化程度
            if primary_theme == "民族文化深度体验":
                commercial_level = attr.get("commercial_level", "")
                if commercial_level == "高":
                    # 商业化高的景点需要额外考虑
                    if any(kw in attr_name for kw in ["古城", "古镇", "文化"]):
                        # 重要的文化景点，即使商业化高也保留，但标记
                        attr["note"] = "商业化程度较高，但文化价值重要"
                        filtered.append(attr)
                    continue
            
            if matches_theme:
                filtered.append(attr)
        
        return filtered
    
    def _organize_attractions(self, attractions, theme):
        """组织景点信息（分组、排序、推荐）"""
        if not attractions:
            return {"groups": [], "recommendations": []}
        
        # 按类型分组
        groups = {}
        for attr in attractions:
            attr_type = attr.get("type", "其他")
            if attr_type not in groups:
                groups[attr_type] = []
            groups[attr_type].append(attr)
        
        # 生成推荐
        recommendations = []
        
        if theme["primary_theme"] == "民族文化深度体验":
            culture_attrs = [a for a in attractions if a.get("type") == "文化"]
            if culture_attrs:
                recommendations.append({
                    "focus": "文化深度体验",
                    "suggestions": [f"重点体验{a['name']}" for a in culture_attrs[:2]],
                    "reason": "符合您对少数民族文化的兴趣"
                })
        
        # 时间分配建议
        total_time = sum([self._parse_time(a.get("time_needed", "2小时")) for a in attractions])
        recommendations.append({
            "focus": "时间安排",
            "suggestions": [f"预计需要{total_time}小时游览所有景点"],
            "reason": "合理规划避免赶路"
        })
        
        return {
            "groups": groups,
            "recommendations": recommendations,
            "total_attractions": len(attractions)
        }
    
    def _parse_time(self, time_str):
        """解析时间字符串为小时数"""
        if "全天" in time_str:
            return 8
        elif "半天" in time_str:
            return 4
        elif "小时" in time_str:
            try:
                return int(time_str.split("-")[0])
            except:
                return 3
        return 2
    
    async def _collect_weather_info(self, destination):
        """收集天气信息"""
        print(f"    → 为{destination}收集天气信息")
        
        weather = self.tools["get_weather_forecast_tool"](destination, "2024-06-01")
        
        return ("weather", destination, weather)
    
    async def _collect_budget_info(self, framework):
        """收集预算信息"""
        print("    → 收集预算信息")
        
        budget_data = self.tools["calculate_budget_breakdown_tool"](framework, framework["total_budget"])
        
        return budget_data
    
    def _assess_data_quality(self, collected_data):
        """评估数据质量"""
        quality_report = {
            "completeness": 0,
            "relevance": 0,
            "timeliness": 0,
            "needs_completion": False,
            "issues": []
        }
        
        total_items = 0
        completed_items = 0
        
        # 检查每个目的地的数据完整性
        for destination, data in collected_data.items():
            if destination == "budget":
                continue
                
            categories = ["transportation", "accommodation", "attractions", "weather"]
            for category in categories:
                total_items += 1
                if category in data and data[category]:
                    completed_items += 1
                else:
                    quality_report["issues"].append(f"{destination}的{category}数据缺失")
        
        # 计算完整性分数
        if total_items > 0:
            quality_report["completeness"] = completed_items / total_items
        
        # 检查是否关键数据缺失
        critical_categories = ["accommodation", "transportation"]
        for dest in [d for d in collected_data.keys() if d != "budget"]:
            for category in critical_categories:
                if category not in collected_data.get(dest, {}) or not collected_data[dest][category]:
                    quality_report["needs_completion"] = True
                    break
        
        return quality_report
    
    def _complete_missing_data(self, collected_data, quality_report):
        """补全缺失数据"""
        print("  阶段2: 补全缺失数据...")
        
        # 这里可以触发重新查询或使用备用数据源
        # 简化示例：标记需要人工干预
        for issue in quality_report["issues"]:
            print(f"    ⚠️ {issue} - 需要进一步查询")
        
        return collected_data
    
    def _apply_constraints_filters(self, collected_data, deep_needs):
        """应用约束条件过滤数据"""
        print("  阶段3: 应用约束条件过滤...")
        
        filtered_data = {}
        constraints = deep_needs.get("constraints", [])
        
        for destination, data in collected_data.items():
            if destination == "budget":
                filtered_data[destination] = data
                continue
            
            filtered_dest_data = {}
            
            # 过滤住宿：基于商业化约束
            if "accommodation" in data:
                accommodation_data = data["accommodation"]
                hotels = accommodation_data.get("hotels", [])
                
                # 应用商业化约束
                commercial_constraint = any(
                    "避免过度商业化景点" in c.get("constraint", "") 
                    for c in constraints if c.get("type") == "软约束"
                )
                
                if commercial_constraint:
                    filtered_hotels = [
                        h for h in hotels 
                        if not any("豪华" in str(f) for f in h.get("features", []))
                    ]
                    if filtered_hotels:
                        accommodation_data["hotels"] = filtered_hotels
                        accommodation_data["filter_note"] = "已过滤过于商业化的酒店选项"
            
            filtered_dest_data = data
            filtered_data[destination] = filtered_dest_data
        
        return filtered_data
    
    def _integrate_cross_tool_data(self, filtered_data):
        """跨工具数据关联与整合"""
        print("  阶段4: 跨工具数据关联...")
        
        integrated = {
            "destinations": {},
            "transportation_network": {},
            "budget_adjustments": [],
            "conflicts": [],
            "opportunities": []
        }
        
        # 为每个目的地创建整合视图
        for destination, data in filtered_data.items():
            if destination == "budget":
                integrated["budget"] = data
                continue
            
            # 整合交通、住宿、景点信息
            dest_integration = {
                "accommodation_options": len(data.get("accommodation", {}).get("hotels", [])),
                "attraction_count": data.get("attractions", {}).get("total_attractions", 0),
                "weather_forecast": data.get("weather", {}),
                "recommended_stay": self._calculate_recommended_stay(data)
            }
            
            # 检查数据一致性
            self._check_data_consistency(destination, data, integrated)
            
            integrated["destinations"][destination] = dest_integration
        
        # 构建交通网络
        integrated["transportation_network"] = self._build_transportation_network(filtered_data)
        
        return integrated
    
    def _calculate_recommended_stay(self, destination_data):
        """计算建议停留时间"""
        attraction_count = destination_data.get("attractions", {}).get("total_attractions", 0)
        
        if attraction_count >= 4:
            return "建议停留2-3天"
        elif attraction_count >= 2:
            return "建议停留1-2天"
        else:
            return "建议停留1天或作为过境地"
    
    def _check_data_consistency(self, destination, data, integrated):
        """检查数据一致性"""
        # 检查天气与活动匹配度
        weather = data.get("weather", {})
        attractions = data.get("attractions", {}).get("groups", {})
        
        if weather.get("condition") in ["中雨", "大雨", "暴雨"] and "户外" in str(attractions):
            integrated["conflicts"].append({
                "destination": destination,
                "issue": "雨天与户外景点冲突",
                "suggestion": "准备室内备用方案或调整行程"
            })
    
    def _build_transportation_network(self, filtered_data):
        """构建交通网络图"""
        # 简化示例：基于目的地之间的交通连接
        network = {
            "昆明": ["大理"],
            "大理": ["昆明", "丽江", "沙溪古镇"],
            "沙溪古镇": ["大理", "丽江"],
            "丽江": ["大理", "沙溪古镇"]
        }
        
        # 添加交通方式建议
        transportation_suggestions = []
        for from_city, to_cities in network.items():
            for to_city in to_cities:
                if from_city in filtered_data and to_city in filtered_data:
                    transport_data_from = filtered_data[from_city].get("transportation", {})
                    
                    suggestion = {
                        "route": f"{from_city} → {to_city}",
                        "recommendation": self._get_route_recommendation(from_city, to_city, transport_data_from)
                    }
                    transportation_suggestions.append(suggestion)
        
        return {
            "connections": network,
            "suggestions": transportation_suggestions
        }
    
    def _get_route_recommendation(self, from_city, to_city, transport_data):
        """获取路线推荐"""
        if from_city == "昆明" and to_city == "大理":
            return "乘坐高铁，约2.5小时，班次频繁"
        elif from_city == "大理" and to_city == "丽江":
            return "乘坐高铁或汽车，高铁约1.5小时"
        elif from_city == "大理" and to_city == "沙溪古镇":
            return "建议包车或拼车，约2-3小时山路"
        else:
            return "建议查询具体交通安排"
    
    def _generate_insights(self, integrated_data, travel_framework, deep_needs):
        """基于所有数据生成洞察"""
        print("  阶段5: 生成综合洞察...")
        
        insights = {
            "key_findings": [],
            "recommendations": [],
            "warnings": [],
            "opportunities": []
        }
        
        # 分析每个目的地的适合度
        for destination, data in integrated_data.get("destinations", {}).items():
            stay_recommendation = data.get("recommended_stay", "")
            attraction_count = data.get("attraction_count", 0)
            
            if attraction_count >= 3:
                insights["key_findings"].append(
                    f"{destination}有{attraction_count}个匹配景点，{stay_recommendation}"
                )
        
        # 预算分析
        budget = integrated_data.get("budget", {})
        if isinstance(budget, dict):
            for category, info in budget.items():
                if isinstance(info, dict) and "ratio" in info:
                    if info["ratio"] > 0.35:
                        insights["warnings"].append(
                            f"{category}占比{info['ratio']*100:.0f}%，可能超出预期"
                        )
        
        # 时间可行性分析
        total_days = travel_framework.get("duration_days", 7)
        destination_count = len(integrated_data.get("destinations", {}))
        
        if destination_count > 3 and total_days < 10:
            insights["warnings"].append(
                f"{total_days}天内安排{destination_count}个目的地可能较紧张"
            )
        
        # 发现机会点
        deep_preferences = deep_needs.get("deep_preferences", [])
        if any("渴望深度文化接触" in str(p) for p in deep_preferences):
            insights["opportunities"].append(
                "发现多个民族文化体验点，可安排深度文化工作坊"
            )
        
        return insights