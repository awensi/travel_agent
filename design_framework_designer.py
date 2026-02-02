class TravelFrameworkDesigner:
    """agent skill:旅行框架设计能力"""

    def design_travel_framework(self, duration, budget, deep_preferences):
        """基于深度需求设计旅行框架"""

        #1 确定旅行主题
        theme = self._determine_travel_theme(deep_preferences)

        #2 目的地匹配
        destinations = self._match_destinations(theme, deep_preferences)

        #3 行程节奏设计
        pacing = self._design_pacing_strategy(duration, deep_preferences)

        #4 预算分配策略
        budget_allocation = self._allocate_budget(budget, theme, destinations)

        #5 风险与妥协点识别
        risk_assessment = self._identify_risk_and_tradeoffs(destinations, deep_preferences)

        #6 生成框架
        framework= {
            "theme": theme,
            "destinations": destinations,
            "duration_days": duration,
            "total_budget": budget,
            "pacing_strategy": pacing,
            "budget_allocation": budget_allocation,
            "risk_assessment": risk_assessment,
            "design_rationale": self._generate_design_rationale(
                theme, destinations, pacing, budget_allocation
            )
        }
        return framework
        
    def _determine_travel_theme(self, deep_preferences):
        #确定旅行主题
        #分析价值优先级，确定旅行主题
        value_priorities = [p["type"] for p in deep_preferences.get("deep_preferences", [])]
        if "体验价值" in value_priorities:
            if any("少数民族文化" in str(p) for p in deep_preferences.get("deep_preferences", [])):
                return {
                    "primary_theme": "民族文化深度体验",
                    "secondary_themes": ["原生态探索", "摄影采风"],
                    "intensity": "深度",  # 深度/中度/轻度
                    "focus": "文化沉浸"
                }
            else:
                return {
                    "primary_theme": "自然风光探索",
                    "secondary_themes": ["户外活动", "生态旅游"],
                    "intensity": "中度",  # 深度/中度/轻度
                    "focus": "自然景观"
                }
        elif "舒适价值" in value_priorities:
            return {
                "primary_theme": "休闲度假",
                "secondary_themes": ["精品住宿", "特色美食"],
                "intensity": "轻度",
                "focus": "放松享受"
            }
        else:
            return {
                "primary_theme": "经典观光",
                "secondary_themes": ["地标打卡", "文化概览"],
                "intensity": "中度",
                "focus": "全面覆盖"
            }
        
    def _match_destinations(self, theme, deep_preferences):
        """匹配目的地"""
        # 基于主题和价值偏好的目的地推荐逻辑
        yunnan_destinations = {
            "大理": {
                "themes": ["民族文化深度体验", "自然风光探索", "休闲度假"],
                "culture_focus": ["白族文化", "古城历史"],
                "commercial_level": "中等",  # 低/中等/高
                "nature_features": ["苍山", "洱海"],
                "accessibility": "高",
                "budget_friendliness": "中等"
            },
            "沙溪古镇": {
                "themes": ["民族文化深度体验", "原生态探索"],
                "culture_focus": ["茶马古道", "古镇生活"],
                "commercial_level": "低",
                "nature_features": ["田园风光"],
                "accessibility": "中等",
                "budget_friendliness": "高"
            },
            "丽江": {
                "themes": ["民族文化深度体验", "经典观光"],
                "culture_focus": ["纳西文化", "世界遗产"],
                "commercial_level": "高",
                "nature_features": ["玉龙雪山"],
                "accessibility": "高", 
                "budget_friendliness": "中等"
            },
            "泸沽湖": {
                "themes": ["自然风光探索", "原生态探索"],
                "culture_focus": ["摩梭文化"],
                "commercial_level": "低",
                "nature_features": ["湖泊", "山脉"],
                "accessibility": "低",
                "budget_friendliness": "中等"
            }
        }

        #基于主题和偏好过滤
        filtered_destinations = {}
        for name, info in yunnan_destinations.items():
            theme_match = theme["primary_theme"] in info["themes"] or theme["primary_theme"]

            #商业化程度过滤
            commercial_filter = True
            if any("追求原生态体验" in str(p) for p in deep_preferences.get("deep_preferences", [])):
                if info["commerical_level"] == "高":
                    commercial_filter = False
            
            #文化匹配
            culture_filter = True
            if any("少数民族文化" in str(p) for p in deep_preferences.get("deep_preference", [])):
                if not info["culture_focus"]:
                    culture_filter = False
            
            if theme_match and commercial_filter and culture_filter:
                filtered_destinations[name] = info

        #选择2-4个目的地，考虑交通便利性
        selected = {}
        for name in ["大理", "沙溪古镇", "丽江"]:  #按照逻辑顺序
            if name in filtered_destinations:
                selected[name] = filtered_destinations[name]
                if len(selected) >= 3:
                    break
        return selected
    
    def _design_pacing_strategy(self, duration, deep_preferences):
        #设计行程节奏
        #分析用户偏好，确定节奏
        pacing_profile = "balanced" #平衡型

        if any("渴望深度文化接触" in str(p) for p in deep_preferences.get("deep_preferences", [])):
            pacing_profile = "immersive" #沉浸型
        elif any("避开大众旅行团" in str(p) for p in deep_preferences.get("deep_preferences", [])):
            pacing_profile = "relaxed" #放松型
        strategies = {
            "immersive": {
                    "description": "深度沉浸式节奏",
                    "nights_per_destination": 3,  # 每个目的地住3晚
                    "daily_activities": 2,  # 每天主要活动2个
                    "free_time_ratio": 0.3,  # 30%自由时间
                    "transfer_days": "最小化"  # 尽量减少交通日
            },
            "balanced": {
                "description": "平衡观光节奏", 
                "nights_per_destination": 2,
                "daily_activities": 3,
                "free_time_ratio": 0.2,
                "transfer_days": "适度安排"
            },
            "relaxed": {
                "description": "放松休闲节奏",
                "nights_per_destination": 3,
                "daily_activities": 1.5,  # 每天1-2个活动
                "free_time_ratio": 0.4,
                "transfer_days": "充足安排"
            }
        }
        strategy = strategies[pacing_profile]
        if duration < 5:
            strategy["description"] += "(紧凑版)"
            strategy["daily_activities"] = min(strategy["daily_activities"] + 0.5, 4)
            strategy["free_time_ratio"] = max[strategy["free_time_ratio"] - 0.1, 0.1]

        return strategy
    
    def _allocate_budget(self, total_budget, theme, destinations):
        """预算分配策略"""
        # 基于主题和目的地的智能预算分配
        base_allocation = {
            "transportation": 0.35,  # 交通
            "accommodation": 0.25,   # 住宿
            "experiences": 0.20,     # 体验活动
            "food": 0.15,            # 餐饮
            "contingency": 0.05      # 应急
        }

        #根据主题调整
        if theme["primary_theme"] == "民族文化深度体验":
            base_allocation["experiences"] += 0.05
            base_allocation["accommodation"] -= 0.05
        elif theme["primary_theme"] == "自然风光探索":
            base_allocation["transportation"] += 0.05
            base_allocation["food"] += 0.05

        #根据目的地商业化程度调整
        commerical_levels = [d["commercial_level"] for d in destinations.values()]
        if "高" in commerical_levels:
            base_allocation["accommodation"] += 0.03
            base_allocation["experiences"] += 0.02
        if "低" in commerical_levels:
            base_allocation["contingency"] += 0.02
        
        #确保总和为1
        total = sum(base_allocation.values())
        for key in base_allocation:
            base_allocation[key] /= total
        
        #转换为具体金额
        detail_allocation = {}
        for category, ratio in base_allocation.items():
            amount = int(total_budget * ratio)
            detail_allocation[category] = {
                "amount": amount,
                "ratio": ratio,
                "rationale": self._get_allocation_rationale(category, ratio, theme)
            }
        return detail_allocation
    
    def _get_allocation_rationale(self, category, ratio, theme):
        #获取预算分配的理由
        rationales = {
            "transportation": {
                "民族文化深度体验": "云南景点分散，交通成本较高，需预留充足",
                "自然风光探索": "需要前往偏远景区，交通费用占比高",
                "default": "机票和当地交通是主要开销"
            },
            "accommodation": {
                "追求原生态体验": "建议选择特色民宿而非豪华酒店",
                "休闲度假": "住宿体验是重点，适当增加预算",
                "default": "7晚住宿是基础支出"
            },
            "experiences": {
                "民族文化深度体验": "文化体验活动是核心价值，重点投入",
                "自然风光探索": "门票和导游费用",
                "default": "景点门票和体验活动"
            }
        }
        if category in rationales:
            if theme["primary_theme"] in rationales[category]:
                return rationales[category][theme["primary_theme"]]
            return rationales[category]["default"]
        return "标准预算分配"
    
    
    def _identify_risk_and_tradeoffs(self, destinations, deep_preferences):
        #识别风险和妥协点
        risk = []
        tradeoffs = []

        #分析目的地组合的风险
        dest_names = list(destinations.keys())

        if "泸沽湖" in dest_names and len(dest_names) > 2:
            risk.append({
                "type": "时间风险",
                "description": "泸沽湖交通不便，往返需要2天，7天行程可能过于紧张",
                "severity": "中",
                "mitigation": "考虑放弃泸沽湖或延长总天数"
            })

        #商业化程度妥协
        culture_pref = any("渴望深度文化接触" in str(p) for p in deep_preferences.get("deep_preferences", []))
        anti_commercial = any("追求原生态体验" in str(p) for p in deep_preferences.get("deep_preferences", []))

        if culture_pref and anti_commercial and "丽江" in dest_names:
            tradeoffs.append({
                "aspect": "商业化程度",
                "compromise": "丽江商业化程度高，但文化价值极高",
                "rationale": "为获取顶级文化体验，需要接受一定商业化",
                "suggestion": "选择丽江古城外围住宿，早晚避开游客高峰"
            })
        
        #预算风险
        if "沙溪古镇" in dest_names and "大理" in dest_names:
            #两地商业化程度较低，可能体验质量高，但是便利性差
            #compromise 危害性  rationale 原理 tradeoffs 取舍
            tradeoffs.append({
                "aspect":"便利性",
                "compromise": "原生态目的地交通和住宿选择较少",
                "rationale": "追求原生态体验需要牺牲部分便利性",
                "suggestion": "提前预订交通和住宿，准备灵活应对"
            })
        
        return {
            "identified_risks": risk,
            "necessary_tradeoffs": tradeoffs,
            "overall_risk_level": "低" if len(risk) == 0 else "中"
        }
    

    def _generate_design_rationale(self, theme, destinations, pacing, budget_allocation):
        #生成设计理由

        dest_list = "，".join(destinations.keys())
        rationale = f"""
        基于您的需求分析，设计了{theme["primary_theme"]}主题的行程框架:

        1、目的地选择({dest_list}):
            - 匹配您对{next(iter(theme['secondary_themes']), '文化体验')}的偏好
           - 平衡文化深度与旅行可行性
           - 考虑商业化程度符合您的要求

        2. 行程节奏 ({pacing['description']})：
           - 每个目的地安排{pacing['nights_per_destination']}晚住宿
           - 每天{pacing['daily_activities']}个主要活动，保留{pacing['free_time_ratio']*100:.0f}%自由时间
           - {pacing['transfer_days']}交通转换
        
        3. 预算分配：
        """

        for category, info in budget_allocation.items():
            rationale += f"   - {category}: {info['amount']}元 ({info['ratio']*100:.0f}%) - {info['rationale']}\n"
        return rationale
    