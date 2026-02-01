from deep_need_analyzer import DeepNeedAnalyzer
from design_framework_designer import TravelFrameworkDesigner
from tool_coordinator import ToolCoordinator

class TravelPlanningAgent:
    """完整的旅行规划智能体"""
    
    def __init__(self):
        # 初始化各种Skill
        self.need_analyzer = DeepNeedAnalyzer()
        self.framework_designer = TravelFrameworkDesigner()
        self.tool_coordinator = None  # 在运行时注入tools
        
        # 工具集合（实际使用时从外部注入）
        self.tools = {
            "search_flights": self._mock_search_flights,
            "search_hotels_tool": self._mock_search_hotels,
            "get_weather_forecast_tool": self._mock_get_weather,
            "calculate_budget_breakdown_tool": self._mock_calculate_budget,
            "get_attraction_info": self._mock_get_attraction_info
        }
        
        # 协调器
        self.tool_coordinator = ToolCoordinator(self.tools)
        
        # 决策历史
        self.decision_log = []
    
    def plan_trip(self, user_request):
        """主要执行流程：完整展示Agent Skill与Tool Use的结合"""
        print("="*60)
        print("🧠 智能旅行规划引擎启动")
        print("="*60)
        
        # ========== 阶段1: 深度需求分析 (Agent Skill) ==========
        print("\n🔍 阶段1: 深度需求分析")
        print("-"*40)
        
        deep_needs = self.need_analyzer.analyze_deep_needs(user_request)
        
        print("📋 表面需求:")
        for need in deep_needs.get("surface_needs", []):
            print(f"  • {need['category']}: {need['value']}")
        
        print("\n💡 深层偏好分析:")
        for pref in deep_needs.get("deep_preferences", []):
            print(f"  • {pref['preference']} (置信度: {pref['confidence']})")
            print(f"    依据: {pref['rationale']}")
        
        print("\n⚖️ 价值优先级排序:")
        for value in deep_needs.get("value_priorities", []):
            print(f"  • {value['value_type']}: 权重 {value['weight']:.2f}")
        
        self._log_decision("deep_needs_analysis", deep_needs)
        
        # ========== 阶段2: 旅行框架设计 (Agent Skill) ==========
        print("\n📐 阶段2: 旅行框架设计")
        print("-"*40)
        
        duration = 7  # 从需求分析中提取
        budget = 8000  # 从需求分析中提取
        
        travel_framework = self.framework_designer.design_travel_framework(
            duration, budget, deep_needs
        )
        
        print(f"🎯 旅行主题: {travel_framework['theme']['primary_theme']}")
        print(f"📍 推荐目的地: {', '.join(travel_framework['destinations'].keys())}")
        print(f"🏃 行程节奏: {travel_framework['pacing_strategy']['description']}")
        
        print("\n💰 预算分配策略:")
        for category, info in travel_framework['budget_allocation'].items():
            print(f"  • {category}: {info['amount']}元 ({info['ratio']*100:.0f}%) - {info['rationale']}")
        
        self._log_decision("framework_design", travel_framework)
        
        # ========== 阶段3: 工具协调与数据收集 (Agent Skill + Tool Use) ==========
        print("\n🛠️ 阶段3: 工具协调与数据收集")
        print("-"*40)
        
        coordinated_data = self.tool_coordinator.coordinate_tools(travel_framework, deep_needs)
        
        print("\n📊 数据收集完成:")
        print(f"  • 收集了{len(coordinated_data['integrated_data'].get('destinations', {}))}个目的地的详细信息")
        print(f"  • 发现{len(coordinated_data['insights'].get('key_findings', []))}个关键发现")
        print(f"  • 生成{len(coordinated_data['insights'].get('recommendations', []))}条推荐")
        
        # ========== 阶段4: 风险评估与优化 (Agent Skill) ==========
        print("\n⚠️ 阶段4: 风险评估与优化")
        print("-"*40)
        
        risks_and_optimizations = self._assess_and_optimize(
            travel_framework, coordinated_data, deep_needs
        )
        
        print("🔍 识别到的风险:")
        for risk in risks_and_optimizations.get("risks", []):
            print(f"  • {risk['description']} (严重性: {risk['severity']})")
            print(f"    缓解措施: {risk['mitigation']}")
        
        print("\n✨ 优化机会:")
        for opp in risks_and_optimizations.get("opportunities", []):
            print(f"  • {opp}")
        
        # ========== 阶段5: 生成最终方案 (Agent Skill) ==========
        print("\n📋 阶段5: 生成最终方案")
        print("-"*40)
        
        final_plan = self._generate_final_plan(
            user_request, deep_needs, travel_framework, 
            coordinated_data, risks_and_optimizations
        )
        
        self._log_decision("final_plan", final_plan)
        
        return final_plan
    
    def _assess_and_optimize(self, framework, coordinated_data, deep_needs):
        """风险评估与优化（Agent Skill）"""
        risks = []
        opportunities = []
        
        # 预算风险评估
        budget = coordinated_data.get("budget", {})
        total_budget = framework.get("total_budget", 0)
        
        if isinstance(budget, dict):
            total_estimated = sum(
                info.get("amount", 0) for info in budget.values() 
                if isinstance(info, dict)
            )
            
            if total_estimated > total_budget * 1.1:  # 超过10%
                risks.append({
                    "type": "预算风险",
                    "description": f"预估费用{total_estimated}元超过预算{total_budget}元的10%",
                    "severity": "高",
                    "mitigation": "建议调整住宿标准或减少目的地"
                })
        
        # 时间可行性评估
        destinations = coordinated_data.get("integrated_data", {}).get("destinations", {})
        total_days = framework.get("duration_days", 0)
        
        estimated_days_needed = 0
        for dest, data in destinations.items():
            stay_rec = data.get("recommended_stay", "")
            if "2-3天" in stay_rec:
                estimated_days_needed += 2.5
            elif "1-2天" in stay_rec:
                estimated_days_needed += 1.5
            else:
                estimated_days_needed += 1
        
        if estimated_days_needed > total_days:
            risks.append({
                "type": "时间风险",
                "description": f"建议行程需要{estimated_days_needed}天，但只有{total_days}天",
                "severity": "中",
                "mitigation": "建议减少目的地或缩短每个地点停留时间"
            })
        
        # 寻找优化机会
        # 1. 基于用户偏好的优化
        deep_preferences = deep_needs.get("deep_preferences", [])
        for pref in deep_preferences:
            if "追求原生态体验" in str(pref):
                opportunities.append("发现非商业化体验：沙溪古镇马帮文化体验")
            if "渴望深度文化接触" in str(pref):
                opportunities.append("推荐参与白族扎染或东巴文字工作坊")
        
        # 2. 基于数据洞察的优化
        insights = coordinated_data.get("insights", {})
        for finding in insights.get("key_findings", []):
            if "匹配景点" in finding:
                opportunities.append(f"根据{finding}，可安排深度游览")
        
        return {
            "risks": risks,
            "opportunities": opportunities,
            "optimization_suggestions": self._generate_optimization_suggestions(risks, opportunities)
        }
    
    def _generate_optimization_suggestions(self, risks, opportunities):
        """生成优化建议"""
        suggestions = []
        
        # 针对风险的优化建议
        for risk in risks:
            if risk["type"] == "预算风险":
                suggestions.append({
                    "area": "预算优化",
                    "suggestion": "考虑将部分住宿从酒店调整为特色民宿",
                    "impact": "预计可节省20-30%住宿费用",
                    "implementation": "已筛选符合要求的民宿选项"
                })
            elif risk["type"] == "时间风险":
                suggestions.append({
                    "area": "时间优化",
                    "suggestion": "将玉龙雪山一日游调整为半日游，上午前往避免排队",
                    "impact": "节省半天时间用于交通或休息",
                    "implementation": "调整行程顺序，上午安排主要景点"
                })
        
        # 基于机会的增强建议
        for opp in opportunities:
            if "文化体验" in opp:
                suggestions.append({
                    "area": "体验增强",
                    "suggestion": "增加民族文化深度体验活动",
                    "impact": "提升旅行文化价值，符合用户深层偏好",
                    "implementation": "联系当地文化机构安排体验"
                })
        
        return suggestions
    
    def _generate_final_plan(self, user_request, deep_needs, framework, coordinated_data, risks_optimizations):
        """生成最终旅行方案（综合所有信息的Agent Skill）"""
        
        # 提取关键信息
        destinations = list(framework["destinations"].keys())
        theme = framework["theme"]["primary_theme"]
        total_budget = framework["total_budget"]
        
        # 构建详细行程
        detailed_itinerary = self._build_detailed_itinerary(
            destinations, framework, coordinated_data
        )
        
        # 生成最终方案
        final_plan = {
            "user_request": user_request,
            "executive_summary": {
                "theme": theme,
                "destinations": destinations,
                "duration": f"{framework['duration_days']}天",
                "total_budget": total_budget,
                "value_proposition": self._generate_value_proposition(theme, deep_needs)
            },
            "deep_needs_analysis": {
                "key_insights": [p["preference"] for p in deep_needs.get("deep_preferences", [])],
                "value_priorities": [v["value_type"] for v in deep_needs.get("value_priorities", [])]
            },
            "detailed_itinerary": detailed_itinerary,
            "budget_breakdown": coordinated_data.get("budget", {}),
            "accommodation_recommendations": self._extract_accommodation_recommendations(coordinated_data),
            "transportation_plan": self._build_transportation_plan(coordinated_data),
            "risk_assessment": {
                "identified_risks": risks_optimizations.get("risks", []),
                "optimization_suggestions": risks_optimizations.get("optimization_suggestions", []),
                "contingency_plans": self._generate_contingency_plans(risks_optimizations.get("risks", []))
            },
            "insights_and_recommendations": coordinated_data.get("insights", {}),
            "implementation_guide": self._generate_implementation_guide(),
            "generation_timestamp": "2024-01-15T10:30:00Z",
            "agent_confidence": 0.85  # 智能体对方案的置信度
        }
        
        return final_plan
    
    def _build_detailed_itinerary(self, destinations, framework, coordinated_data):
        """构建详细行程（复杂的规划逻辑）"""
        itinerary = []
        
        # 智能行程安排逻辑
        day_counter = 1
        current_location = "北京"
        
        # 第一天：出发
        itinerary.append({
            "day": day_counter,
            "date": "2024-06-01",
            "location": f"{current_location} → 昆明 → 大理",
            "focus": "交通日，适应环境",
            "morning": "乘坐MU5678航班从北京飞往昆明（14:00-17:45）",
            "afternoon": "从昆明机场乘高铁至大理（约2小时）",
            "evening": "入住大理古城民宿，晚上逛大理古城夜景",
            "accommodation": self._get_accommodation_for_day("大理", coordinated_data),
            "meals": "晚餐：大理古城内白族特色餐厅",
            "estimated_cost": 1200,
            "travel_tips": "建议提前1.5小时到达机场办理值机"
        })
        day_counter += 1
        current_location = "大理"
        
        # 后续天数根据目的地智能安排
        for i, destination in enumerate(destinations):
            if destination == current_location:
                # 目的地停留天数计算
                stay_days = 2 if len(destinations) == 3 else 3
                
                for day_in_dest in range(stay_days):
                    day_plan = self._generate_day_plan(
                        day_counter, destination, day_in_dest+1, 
                        coordinated_data, framework["theme"]
                    )
                    itinerary.append(day_plan)
                    day_counter += 1
        
        return itinerary
    
    def _get_accommodation_for_day(self, destination, coordinated_data):
        """获取当日住宿推荐"""
        # 从协调数据中提取住宿推荐
        dest_data = coordinated_data.get("raw_data", {}).get(destination, {})
        accommodation = dest_data.get("accommodation", {})
        hotels = accommodation.get("hotels", [])
        
        if hotels:
            best_hotel = hotels[0]  # 推荐分数最高的
            return f"{best_hotel.get('name', '待定')} ({best_hotel.get('price_per_night', '?')}元/晚)"
        return "待定"
    
    def _generate_day_plan(self, day_number, destination, day_in_dest, coordinated_data, theme):
        """生成单日行程计划"""
        # 基于主题和目的地信息生成个性化行程
        dest_data = coordinated_data.get("raw_data", {}).get(destination, {})
        attractions = dest_data.get("attractions", {}).get("groups", {})
        
        # 根据主题选择活动
        if theme["primary_theme"] == "民族文化深度体验":
            activities = self._generate_cultural_day(attractions, day_in_dest)
        elif theme["primary_theme"] == "自然风光探索":
            activities = self._generate_nature_day(attractions, day_in_dest)
        else:
            activities = self._generate_general_day(attractions, day_in_dest)
        
        return {
            "day": day_number,
            "date": f"2024-06-{day_number:02d}",
            "location": destination,
            "focus": activities["focus"],
            "morning": activities["morning"],
            "afternoon": activities["afternoon"], 
            "evening": activities["evening"],
            "accommodation": self._get_accommodation_for_day(destination, coordinated_data),
            "estimated_cost": 300 + day_in_dest * 50,  # 简单模拟
            "cultural_tip": activities.get("cultural_tip", "")
        }
    
    def _generate_cultural_day(self, attractions, day_in_dest):
        """生成文化体验日行程"""
        cultural_activities = attractions.get("文化", [])
        
        if day_in_dest == 1:
            return {
                "focus": "文化初探与古城体验",
                "morning": f"参观{cultural_activities[0]['name'] if cultural_activities else '当地文化景点'}，了解历史文化",
                "afternoon": "体验传统手工艺制作（如扎染、陶艺）",
                "evening": "观看民族歌舞表演，品尝特色美食",
                "cultural_tip": "与当地手工艺人交流，了解传统技艺背后的文化故事"
            }
        else:
            return {
                "focus": "深度文化沉浸",
                "morning": "走访当地村落，体验原生态生活",
                "afternoon": "参加民族文化工作坊，学习传统技艺",
                "evening": "与当地人共进晚餐，深入交流",
                "cultural_tip": "尝试学习几句当地方言或民歌，深度融入"
            }
    
    def _generate_value_proposition(self, theme, deep_needs):
        """生成价值主张"""
        value_points = []
        
        # 基于主题的价值点
        if theme == "民族文化深度体验":
            value_points.extend([
                "深度接触少数民族文化，非表面观光",
                "参与式体验而非被动观看",
                "避开商业化陷阱，体验原生态文化"
            ])
        
        # 基于深层需求的价值点
        for pref in deep_needs.get("deep_preferences", []):
            if "追求原生态体验" in str(pref):
                value_points.append("精心筛选低商业化程度的景点和体验")
            if "渴望深度文化接触" in str(pref):
                value_points.append("安排与当地人的深度交流机会")
        
        return " | ".join(value_points)
    
    def _extract_accommodation_recommendations(self, coordinated_data):
        """提取住宿推荐"""
        recommendations = []
        
        for destination, data in coordinated_data.get("raw_data", {}).items():
            if destination == "budget":
                continue
            
            accommodation = data.get("accommodation", {})
            hotels = accommodation.get("hotels", [])
            
            if hotels:
                best_hotel = hotels[0]
                recommendations.append({
                    "destination": destination,
                    "name": best_hotel.get("name"),
                    "price_per_night": best_hotel.get("price_per_night"),
                    "features": best_hotel.get("features", []),
                    "recommendation_reason": accommodation.get("recommendation_strategy", "")
                })
        
        return recommendations
    
    def _build_transportation_plan(self, coordinated_data):
        """构建交通计划"""
        network = coordinated_data.get("integrated_data", {}).get("transportation_network", {})
        
        return {
            "inter_city": network.get("suggestions", []),
            "intra_city": "主要推荐包车或电动车，灵活方便",
            "estimated_cost": "约1500-2000元（含机票、火车、当地交通）",
            "booking_tips": [
                "机票建议提前30天预订",
                "云南高铁票建议提前7天预订",
                "当地包车可提前1-2天预订"
            ]
        }
    
    def _generate_contingency_plans(self, risks):
        """生成应急计划"""
        contingencies = []
        
        for risk in risks:
            if risk["type"] == "预算风险":
                contingencies.append({
                    "scenario": "实际费用超出预算10%以上",
                    "action": "启动B计划：减少购物支出，选择经济型餐饮，取消非必要体验项目"
                })
            elif risk["type"] == "时间风险":
                contingencies.append({
                    "scenario": "交通延误或景点游览超时",
                    "action": "动态调整：保留1-2个备用景点，可随时替换；准备快速餐饮方案"
                })
        
        # 通用应急计划
        contingencies.extend([
            {
                "scenario": "天气不佳影响户外活动",
                "action": "替换为室内文化体验：博物馆、手工作坊、茶艺体验"
            },
            {
                "scenario": "身体状况不适",
                "action": "安排轻松行程：古城漫步、茶馆休息、SPA放松"
            }
        ])
        
        return contingencies
    
    def _generate_implementation_guide(self):
        """生成实施指南"""
        return {
            "booking_timeline": [
                {"timing": "提前30天", "action": "预订机票"},
                {"timing": "提前15天", "action": "预订主要城市间交通"},
                {"timing": "提前7天", "action": "预订住宿和主要景点门票"},
                {"timing": "提前1天", "action": "确认所有预订，下载电子票"}
            ],
            "packing_list": [
                "必需品：身份证、现金、银行卡、手机充电器",
                "衣物：轻便透气衣物、防晒外套、舒适徒步鞋",
                "防护：防晒霜、太阳镜、帽子、雨具",
                "药品：常用药、高原反应药物（如前往高海拔地区）",
                "数码：相机、充电宝、转换插头"
            ],
            "cultural_etiquette": [
                "尊重当地少数民族风俗习惯",
                "拍摄人物前先征得同意",
                "进入宗教场所保持肃静，遵守规定",
                "尝试学习简单问候语：'你好'（白族：'诺苏'）"
            ]
        }
    
    def _log_decision(self, stage, data):
        """记录决策过程"""
        self.decision_log.append({
            "stage": stage,
            "timestamp": "2024-01-15T10:30:00Z",
            "data_snapshot": str(data)[:200] + "..." if len(str(data)) > 200 else str(data)
        })
    
    # ========== 模拟工具方法 ==========
    def _mock_search_flights(self, departure_city, arrival_city, **kwargs):
        """模拟航班搜索工具"""
        return [
            {
                "airline": "中国国航",
                "flight_no": "CA1234",
                "departure_time": "08:00",
                "arrival_time": "11:30",
                "price": 1200,
                "class": "经济舱"
            },
            {
                "airline": "东方航空",
                "flight_no": "MU5678",
                "departure_time": "14:00",
                "arrival_time": "17:45",
                "price": 1050,
                "class": "经济舱"
            }
        ]
    
    def _mock_search_hotels(self, city, check_in_date, check_out_date, 
                           budget_per_night, keywords=None):
        """模拟酒店搜索工具"""
        hotels = [
            {
                "name": "大理古城民宿",
                "price_per_night": 280,
                "rating": 4.5,
                "features": ["古城内", "纳西族风格", "观苍山", "安静"],
                "distance_to_attractions": {"大理古城": 0.1}
            },
            {
                "name": "丽江束河古镇客栈",
                "price_per_night": 350,
                "rating": 4.7,
                "features": ["安静", "庭院式", "近束河古镇", "文化特色"],
                "distance_to_attractions": {"束河古镇": 0.3}
            }
        ]
        
        if keywords:
            filtered = []
            for hotel in hotels:
                if any(any(kw in feature for kw in keywords) for feature in hotel["features"]):
                    filtered.append(hotel)
            return filtered
        
        return hotels
    
    def _mock_get_weather(self, location, date):
        """模拟天气查询工具"""
        import random
        weather_conditions = ["晴", "多云", "小雨", "中雨", "阴"]
        
        return {
            "date": date,
            "location": location,
            "temperature_high": random.randint(15, 25),
            "temperature_low": random.randint(5, 15),
            "condition": random.choice(weather_conditions),
            "precipitation_probability": random.randint(0, 80)
        }
    
    def _mock_calculate_budget(self, itinerary, total_budget):
        """模拟预算计算工具"""
        return {
            "transportation": {"amount": 2400,}
        }