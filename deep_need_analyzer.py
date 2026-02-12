import json
from openai import OpenAI

class DeepNeedAnalyzer:

    def __init__(self, client: OpenAI):
        self.model_name = "qwen-max"
        self.client = client


    def analyze_deep_needs(self, user_request):
        """
        Docstring for analyze_deep_needs
        分析用户的深层次需求和隐含偏好
        不仅仅是表面的关键词匹配，而是理解用户的真实意图和偏好
        :param self: Description
        :param user_request: Description
        """
        #模拟LLM进行意图识别和偏好推理
        analysis_result = {
            "surface_needs":[], #表面需求
            "deep_preferences":[], #深层偏好
            "constraints":[], #限制条件
            "unstated_needs": [], #未明说的需求
            "value_prrorities": [] #价值优先级
        }
        #1解析表面需求
        analysis_result["surface_needs"] = self._extract_surface_needs(user_request)

        #2推理深层偏好
        analysis_result["deep_preferences"] = self._infer_deep_preferences(
            user_request,
            analysis_result["surface_needs"]
        )
        #3 识别约束条件
        analysis_result["constraints"] = self._identify_constraints(user_request)

        #4 预测未明说需求
        analysis_result["unstated_needs"] = self._predict_unstated_needs(user_request)

        #5 价值排序
        analysis_result["value_priorities"] = self._rank_value_priorities(analysis_result["deep_preferences"])
        return analysis_result
    
    def _extract_surface_needs(self, user_request):
        """
        Docstring for _extract_surface_needs
        提取表面需求（基础NLP能力）
        :param self: Description
        :param user_request: Description
        """

        #简化为关键词提取，实际会使用更复杂的NLP模型
        # keywords = {
        #     "地点": ["大理", "丽江", "昆明", "云南", "昆明", "石林", "滇池", "洱海", "玉龙雪山"],
        #     "预算": ["20000", "15000", "10000", "8000", "6000", "5000"],
        #     "排除": ["商业化", "商业化的", "不要商业化", "避免商业化"],
        #     "兴趣": ["文化", "少数民族", "民族文化", "自然风光", "风景", "景色"]
        # }

        surface_needs = []
        # for category, terms in keywords.items():
        #     for term in terms:
        #         if term in user_request:
        #             surface_needs.append({
        #                 "category": category,
        #                 "value": term,
        #                 "confidence": 0.9
        #             })
        #             break


        tools = [
            {
                "type":"function",
                "function":{
                    "name":"extract_surface_needs",
                    "description":"从请求中提取地点、预算、排除、兴趣四个特征",
                    "parameters": {
                        "type": "object",
                        "properties":{
                            "地点":{
                                "type":  "list",
                                "description":"请求中描述的地点信息"
                            },
                            "预算": {
                                "type": "list",
                                "description": "请求中描述的有关预算的信息"
                            },
                            "排除": {
                                "type": "list",
                                "description":"请求中描述的需要排除，不感兴趣的信息"
                            },
                            "兴趣":{
                                "type":"list",
                                "description":"请求中描述的比较感兴趣的信息"
                            }
                        },
                        "required":["地点","预算","排除","兴趣"]
                    }
                }
            }
        ]

        try:
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {
                        "role":"user",
                        "content": f"请提取出请求的关键特征信息: {user_request}"
                    }
                ],
                tools= tools
            )
            tools_call = response.choices[0].message.tool_calls[0]
            arguments = json.loads(tools_call.function.arguments)
            surface_needs.append(arguments)
            return surface_needs
        except Exception as e:
            return ""
        
    
    def _infer_deep_preferences(self, user_request, surface_needs):
        #推理深层偏好（高级认知能力）,需要根据user_request调用ai的接口，进行推演
        """使用工具调用获得标准化输出"""
        deep_preferences = []
        tools = [
            {
                "type":"function",
                "function":{
                    "name":"extract_consumption_preference",
                    "description":"从请求中提取消费者的多个特征，并根据请求中的证据，总结出人群的消费倾向，对消费倾向给出相应的置信度",
                    "parameters":{
                        "type":"object",
                        "properties":{
                            "type":{
                                "type":"string",
                                "description":"分析总结消费者的消费特征类型,例如消费偏好，人群偏好，体验偏好等"
                            },
                            "preference": {
                                "type": "string",
                                "description":"根据消费者的请求，推断消费者的消费倾向"
                            },
                            "confidence": {
                                "type": "number",
                                "description":"分析消费特征类型的置信度，范围0-1"
                            },
                            "rationale": {
                                "type": "string",
                                "description": "利用请求中的关键词语证据，为消费者的消费倾向提供证据"
                            }
                        },
                        "required":["type","preference","confidence","rationale"]
                    }
                }
            }
        ]
        try:
            response = self.client.chat.completions.create(
                model = self.model_name,
                messages = [
                    {
                        "role": "user",
                        "content": f"请分析以下请求的消费偏好: {user_request}"
                    }
                ],
                tools = tools,
                temperature=0.5
                # ,
                # tool_choice = {
                #     "type":"function",
                #     "function": {
                #         "name": "extract_consumption_preference"
                #     }
                # }
            )
            print(response)
            #解析工具调用结果
            tool_call = response.choices[0].message.tool_calls[0]
            arguments = json.loads(tool_call.function.arguments)
            print(f"深层次的分析结果: {arguments}")
            deep_preferences.append(arguments)
            return deep_preferences
        except Exception as e:
            print(f"Error: {e}")
            return self._init_default_need(surface_needs)
        
    def _init_default_need(self, surface_needs):
        deep_preferences = []

        #推理1 从不太想去商业化的地方 推断
        if any("商业化" in n["value"] or "商业" in n["value"] for n in surface_needs if n["category"] == "排除"):
            deep_preferences.extend([
                {
                    "type": "体验偏好",
                    "preference": "追求原生态体验",
                    "confidence": 0.85,
                    "rationale": "用户明确提到避免商业化，说明更喜欢未过度开发的景点"
                },
                {
                    "type": "人群偏好", 
                    "preference": "避开大众旅游团",
                    "confidence": 0.8,
                    "rationale": "商业化通常与旅行团聚集相关"
                },
                {
                    "type": "消费偏好",
                    "preference": "重视体验价值而非商业设施",
                    "confidence": 0.75,
                    "rationale": "反商业化可能意味着更愿意为文化体验而非购物付费"
                }
            ])
            
        #推理2 从少数民族文化推断
        if any("少数民族文化" in n["value"] or "文化" in n["value"] for n in surface_needs if n["category"] == "兴趣"):
            deep_preferences.extend([
                {
                    "type": "文化偏好",
                    "preference": "渴望深度文化接触",
                    "confidence": 0.9,
                    "rationale": "明确提到少数民族文化，说明对文化内涵有需求"
                },
                {
                    "type": "活动偏好",
                    "preference": "可能喜欢参与式文化体验",
                    "confidence": 0.7,
                    "rationale": "从看文化到体验文化的潜在需求"
                }
            ])

        #推理3 从预算和时间推断
        budget = next((n for n in surface_needs if n["category"] == "预算"), None)
        
        if budget and "8000" in budget["value"]:
            deep_preferences.append({
                "type": "消费模式",
                "preference": "追求性价比而非奢华",
                "confidence": 0.8,
                "rationale": "7天8000元预算表明中等消费水平，重视性价比"
            })
        return deep_preferences

        
        
    def _identify_constraints(self, user_request):
        tools = [
            {
                "type":"function",
                "function": {
                    "name":"identify_constraint_info",
                    "description":"从请求中获取约束条件，包含硬约束（必须遵守）、软约束(尽量满足，可部分妥协)、推断约束(根据请求推断得出)",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "硬约束": {
                                "type":"list",
                                "description": "请求中必须要遵守的规则"
                            },
                            "软约束" : {
                                "type": "list",
                                "description": "请求中尽量满足，可部分妥协的条件约束"
                            },
                            "推断约束":{
                                "type":"list",
                                "description": "从请求中推断出来的约束条件"
                            }   
                        },
                        "required":["硬约束","软约束","推断约束"]
                    }
                }
            }
        ]
        response = self.client.chat.completions.create(
            model= self.model_name,
            messages=[
                {
                    "role": "user",
                    "content": f"从分析一下请求中的约束条件：{user_request}"
                }
            ],
            tools= tools
        )
        tools_call = response.choices[0].message.tool_calls[0]
        arguments = json.loads(tools_call.function.arguments)
        hard_strict_array = arguments.get("硬约束")
        soft_strict_array = arguments.get("软约束")
        mark_strict_array = arguments.get("推断约束")
        constaints_array = []
        
        if hard_strict_array is not None:
            for strict in hard_strict_array:
                constaint = {
                    "type": "硬约束",
                    "constraint": strict,
                    "strictness": "必须遵守"
                }
                constaints_array.append(constaint)

        for strict in soft_strict_array:
            constaint = {
                "type": "软约束",
                "constraint": strict,
                "strictness": "尽量满足，可部分妥协"
            }
            constaints_array.append(constaint)
        
        for strict in mark_strict_array:
            constaint = {
                "type": "推断约束",
                "constraint": strict,
                "strictness": "根据请求推断得出"
            }
            constaints_array.append(constaint)
        

        return constaints_array
    
    def _predict_unstated_needs(self, user_request):
        #预测用户为明说的需求
        #基于旅游心理学和用户画像的预测
        unstated_needs = [
            {
                "need": "希望获得独特的旅行记忆",
                "confidence": 0.8,
                "evidence": "选择云南而非常规热门目的地"
            },
            {
                "need": "可能对摄影感兴趣",
                "confidence": 0.6,
                "evidence": "提及自然风光，云南是摄影胜地"
            },
            {
                "need": "可能需要网络连接分享体验",
                "confidence": 0.7,
                "evidence": "现代旅行者的普遍需求"
            },
            {
                "need": "可能对当地美食有兴趣但未提及",
                "confidence": 0.65,
                "evidence": "文化体验通常包含饮食文化"
            }
        ]
        return unstated_needs
    
    def _rank_value_priorities(self, deep_preferences):
        #价值排序（什么对用户最重要）
        #基于理由心理学模型的优先排序
        priority_model = {
            "体验价值": ["追求原生态体验", "渴望深度文化接触", "获得独特旅行记忆"],
            "舒适价值": ["避开大众旅游团", "偏好安静住宿环境"],
            "经济价值": ["追求性价比而非奢华"],
            "时间价值": ["高效行程安排", "避免交通浪费时间"]
        }
        value_priorities = []
        for value_type, indicators in priority_model.items():
            matching_prefs = [p for p in deep_preferences if p["preference"] in indicators]
            if matching_prefs:
                value_priorities.append({
                    "value_type": value_type,
                    "weight": len(matching_prefs) * 0.2,
                    "indicators": [p["preference"] for p in matching_prefs]
                })

        #按权重排序
        value_priorities.sort(key=lambda x: x["weight"], reverse=True)
        return value_priorities
    
if __name__ == "__main__":
    client = OpenAI(
        api_key="sk-8de1af2c320640409f98ffd65352f8d5",
        base_url="https://dashscope.aliyuncs.com/compatible-mode/v1"
    )
    need_analyzer = DeepNeedAnalyzer(client=client)
    surface_needs = []
    result = need_analyzer._infer_deep_preferences("我想去云南旅游，旅游时间在8天，预算八千块，对人文景观这些地方感兴趣，希望度过一个比较悠闲，不赶时间的旅行时光", surface_needs)
    print(f"the analyser result is {result}")