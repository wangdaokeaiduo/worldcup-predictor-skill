#!/usr/bin/env python3
"""
世界杯预测引擎 - 自我进化记录本 (Evolution Ledger)

灵感来源：Microsoft SkillOpt (rollout → reflect → aggregate → select → update → evaluate)

功能：
1. 记录每次预测的完整数据（预测比分、概率、关键判断依据）
2. 记录真实比赛结果
3. 计算预测准确度评分
4. 生成"反思报告"（哪里预测对了、哪里错了、为什么错）
5. 提取"进化洞察"（哪些维度的权重需要调整）
"""

import json
import os
import sys
from datetime import datetime

LEDGER_FILE = os.path.join(os.path.dirname(__file__), '..', 'prediction_ledger.json')

def load_ledger():
    """加载预测记录本"""
    if os.path.exists(LEDGER_FILE):
        with open(LEDGER_FILE, 'r', encoding='utf-8') as f:
            ledger = json.load(f)
        # === 向后兼容：如果旧记录本缺少新维度，自动补充 ===
        default_weights = {
            "player_status": 0.20,
            "recent_form": 0.20,
            "head_to_head": 0.10,
            "tactical_fit": 0.10,
            "goalkeeper": 0.05,
            "fatigue_schedule": 0.05,
            "set_pieces": 0.05,
            "match_stakes": 0.05,
            "odds_market": 0.08,
            "squad_depth": 0.05,
            "elo_ranking": 0.04,
            "external_factors": 0.03
        }
        for key, val in default_weights.items():
            if key not in ledger["model_params"]["dimension_weights"]:
                ledger["model_params"]["dimension_weights"][key] = val
        return ledger
    return {
        "version": "2.0",
        "predictions": [],
        "evolution_insights": [],
        "model_params": {
            "dimension_weights": {
                "player_status": 0.20,        # 核心球员状态
                "recent_form": 0.20,           # 近期比赛表现
                "head_to_head": 0.10,          # 历史交锋
                "tactical_fit": 0.10,          # 战术克制
                "goalkeeper": 0.05,            # 门将因素
                "fatigue_schedule": 0.05,      # 体能疲劳/赛程密度
                "set_pieces": 0.05,            # 定位球能力
                "match_stakes": 0.05,          # 比赛性质/动力不对称
                "odds_market": 0.08,           # 赔率数据
                "squad_depth": 0.05,           # 替补深度
                "elo_ranking": 0.04,           # Elo排名
                "external_factors": 0.03       # 场外因素
            },
            "correction_factors": {
                "home_advantage": 0.05,
                "form_bonus": 0.08,
                "injury_penalty": 0.10,
                "psychology_bonus": 0.04,
                "tactical_bonus": 0.06
            },
            "total_predictions": 0,
            "correct_result_count": 0,
            "correct_score_count": 0,
            "avg_score_deviation": 0.0
        }
    }

def save_ledger(ledger):
    """保存预测记录本"""
    os.makedirs(os.path.dirname(LEDGER_FILE), exist_ok=True)
    with open(LEDGER_FILE, 'w', encoding='utf-8') as f:
        json.dump(ledger, f, ensure_ascii=False, indent=2)
    print(f"✅ 预测记录本已保存到: {LEDGER_FILE}")

def add_prediction(team_a, team_b, predicted_score_a, predicted_score_b,
                   win_prob_a, draw_prob, win_prob_b,
                   confidence, key_reasoning):
    """记录一条新预测"""
    ledger = load_ledger()
    prediction = {
        "id": len(ledger["predictions"]) + 1,
        "timestamp": datetime.now().isoformat(),
        "match": f"{team_a} vs {team_b}",
        "team_a": team_a,
        "team_b": team_b,
        "predicted_score": {"team_a": predicted_score_a, "team_b": predicted_score_b},
        "predicted_probs": {"win_a": win_prob_a, "draw": draw_prob, "win_b": win_prob_b},
        "confidence": confidence,
        "key_reasoning": key_reasoning,
        "dimension_weights_used": ledger["model_params"]["dimension_weights"].copy(),
        "actual_result": None,
        "reflection": None,
        "score": None
    }
    ledger["predictions"].append(prediction)
    ledger["model_params"]["total_predictions"] += 1
    save_ledger(ledger)
    print(f"📝 已记录预测: {team_a} {predicted_score_a}:{predicted_score_b} {team_b} (信心: {confidence}/5)")
    return prediction["id"]

def record_actual_result(prediction_id, actual_score_a, actual_score_b):
    """记录真实比赛结果并触发反思"""
    ledger = load_ledger()

    # 找到对应的预测
    pred = None
    for p in ledger["predictions"]:
        if p["id"] == prediction_id:
            pred = p
            break

    if pred is None:
        print(f"❌ 未找到预测ID: {prediction_id}")
        return

    pred["actual_result"] = {"team_a": actual_score_a, "team_b": actual_score_b}

    # === 计算预测评分 ===
    score = 0
    pa, pb = pred["predicted_score"]["team_a"], pred["predicted_score"]["team_b"]

    # 比分完全正确: +100分
    if pa == actual_score_a and pb == actual_score_b:
        score = 100
        ledger["model_params"]["correct_score_count"] += 1
        ledger["model_params"]["correct_result_count"] += 1
    else:
        # 胜平负结果正确: +50分
        pred_result = "draw" if pa == pb else ("win_a" if pa > pb else "win_b")
        actual_result = "draw" if actual_score_a == actual_score_b else ("win_a" if actual_score_a > actual_score_b else "win_b")
        if pred_result == actual_result:
            score += 50
            ledger["model_params"]["correct_result_count"] += 1

        # 总进球数偏差: 最高+30分
        pred_total = pa + pb
        actual_total = actual_score_a + actual_score_b
        goal_diff = abs(pred_total - actual_total)
        score += max(0, 30 - goal_diff * 10)

        # 比分接近度: 最高+20分
        score_diff = abs(pa - actual_score_a) + abs(pb - actual_score_b)
        score += max(0, 20 - score_diff * 5)

    pred["score"] = score

    # === 生成反思报告 ===
    reflection = generate_reflection(pred, actual_score_a, actual_score_b)
    pred["reflection"] = reflection

    # === 更新模型参数（自我进化） ===
    update_model_params(ledger, pred, actual_score_a, actual_score_b)

    # 更新平均偏差
    total = ledger["model_params"]["total_predictions"]
    deviations = []
    for p in ledger["predictions"]:
        if p["actual_result"]:
            dev = abs(p["predicted_score"]["team_a"] - p["actual_result"]["team_a"]) + \
                  abs(p["predicted_score"]["team_b"] - p["actual_result"]["team_b"])
            deviations.append(dev)
    if deviations:
        ledger["model_params"]["avg_score_deviation"] = sum(deviations) / len(deviations)

    save_ledger(ledger)
    print(f"✅ 已记录真实结果并生成反思: {pred['team_a']} {actual_score_a}:{actual_score_b} {pred['team_b']}")
    print(f"📊 预测评分: {score}/100")
    return reflection

def generate_reflection(pred, actual_a, actual_b):
    """生成预测反思报告"""
    pa, pb = pred["predicted_score"]["team_a"], pred["predicted_score"]["team_b"]
    reflection = {
        "timestamp": datetime.now().isoformat(),
        "prediction_accuracy": pred["score"],
        "what_was_right": [],
        "what_went_wrong": [],
        "root_causes": [],
        "dimension_adjustments": {}
    }

    pred_result = "draw" if pa == pb else ("win_a" if pa > pb else "win_b")
    actual_result = "draw" if actual_a == actual_b else ("win_a" if actual_a > actual_b else "win_b")

    # 判断对了什么
    if pred_result == actual_result:
        reflection["what_was_right"].append(f"✅ 胜平负方向判断正确 (预测: {pred_result}, 实际: {actual_result})")
    if pa == actual_a:
        reflection["what_was_right"].append(f"✅ {pred['team_a']}进球数完全命中 ({pa}球)")
    if pb == actual_b:
        reflection["what_was_right"].append(f"✅ {pred['team_b']}进球数完全命中 ({pb}球)")
    if abs(pa + pb - actual_a - actual_b) <= 1:
        reflection["what_was_right"].append(f"✅ 总进球数预测接近 (预测{pa+pb}球 vs 实际{actual_a+actual_b}球)")

    # 判断错了什么
    if pred_result != actual_result:
        reflection["what_went_wrong"].append(f"❌ 胜平负方向判断错误 (预测: {pred_result}, 实际: {actual_result})")
        reflection["root_causes"].append("可能高估/低估了某支球队的实力或状态")
    if abs(pa - actual_a) >= 2:
        reflection["what_went_wrong"].append(f"❌ {pred['team_a']}进球数偏差过大 (预测{pa}球 vs 实际{actual_a}球)")
    if abs(pb - actual_b) >= 2:
        reflection["what_went_wrong"].append(f"❌ {pred['team_b']}进球数偏差过大 (预测{pb}球 vs 实际{actual_b}球)")
    if pa + pb < actual_a + actual_b - 1:
        reflection["root_causes"].append("低估了比赛的进攻性/节奏，泊松模型的λ值可能偏低")
        reflection["dimension_adjustments"]["recent_form"] = "+3%"
    if pa + pb > actual_a + actual_b + 1:
        reflection["root_causes"].append("高估了比赛的进攻性，可能忽视了防守因素")
        reflection["dimension_adjustments"]["tactical_fit"] = "+3%"

    # 基于概率预测质量的反思
    probs = pred["predicted_probs"]
    if actual_result == "win_a" and probs["win_a"] < 0.3:
        reflection["root_causes"].append(f"严重低估了{pred['team_a']}的获胜概率 (仅{probs['win_a']*100:.1f}%)")
        reflection["dimension_adjustments"]["player_status"] = "+5% (需更重视核心球员的临场发挥)"
    if actual_result == "win_b" and probs["win_b"] < 0.3:
        reflection["root_causes"].append(f"严重低估了{pred['team_b']}的获胜概率 (仅{probs['win_b']*100:.1f}%)")
    if actual_result == "draw" and probs["draw"] < 0.15:
        reflection["root_causes"].append("低估了平局的可能性，可能两队实力比预估的更接近")

    return reflection

def update_model_params(ledger, pred, actual_a, actual_b):
    """基于反思结果更新模型参数（SkillOpt式的梯度更新，12维版本）"""
    weights = ledger["model_params"]["dimension_weights"]
    learning_rate = 0.02  # 小步迭代，避免过拟合

    pa, pb = pred["predicted_score"]["team_a"], pred["predicted_score"]["team_b"]
    pred_result = "draw" if pa == pb else ("win_a" if pa > pb else "win_b")
    actual_result = "draw" if actual_a == actual_b else ("win_a" if actual_a > actual_b else "win_b")

    # --- 规则1：方向判断错误 ---
    if pred_result != actual_result:
        # 增加"近期状态"和"核心球员"的权重
        weights["player_status"] = min(0.35, weights["player_status"] + learning_rate)
        weights["recent_form"] = min(0.35, weights["recent_form"] + learning_rate)
        # 降低 Elo/排名的权重（长期指标在短期预测中可能不够敏感）
        weights["elo_ranking"] = max(0.02, weights["elo_ranking"] - learning_rate)
        # 🆕 同时上调 match_stakes（动力不对称可能是被忽视的因素）
        weights["match_stakes"] = min(0.35, weights["match_stakes"] + learning_rate)
        # 🆕 同时上调 goalkeeper（门将可能是比赛的胜负手）
        weights["goalkeeper"] = min(0.35, weights["goalkeeper"] + learning_rate)

    # --- 规则2：进球数偏差大 ---
    goal_deviation = (actual_a + actual_b) - (pa + pb)
    if abs(goal_deviation) >= 2:
        # 增加"战术克制"权重
        weights["tactical_fit"] = min(0.35, weights["tactical_fit"] + learning_rate)
        weights["odds_market"] = min(0.35, weights["odds_market"] + learning_rate)
        # 🆕 定位球经常是额外进球的来源
        weights["set_pieces"] = min(0.35, weights["set_pieces"] + learning_rate)

    # --- 规则3：淘汰赛阶段加大 fatigue_schedule 和 squad_depth 权重 ---
    key_reasoning = pred.get("key_reasoning", "")
    knockout_keywords = ["淘汰赛", "1/8", "1/4", "半决赛", "决赛", "knockout",
                         "round of 16", "quarter", "semi-final", "final"]
    is_knockout = any(kw in str(key_reasoning).lower() for kw in knockout_keywords)
    if is_knockout:
        weights["fatigue_schedule"] = min(0.35, weights["fatigue_schedule"] + learning_rate)
        weights["squad_depth"] = min(0.35, weights["squad_depth"] + learning_rate)

    # --- 保持所有权重的上下限约束 ---
    for key in weights:
        weights[key] = max(0.02, min(0.35, weights[key]))

    # --- 归一化权重（总和为1.0）---
    total_weight = sum(weights.values())
    for key in weights:
        weights[key] = round(weights[key] / total_weight, 4)

    # 记录进化洞察
    insight = {
        "timestamp": datetime.now().isoformat(),
        "match": pred["match"],
        "score": pred["score"],
        "weights_after": weights.copy(),
        "lesson": pred["reflection"]["root_causes"] if pred["reflection"] else []
    }
    ledger["evolution_insights"].append(insight)

def get_review_report():
    """生成历史预测回顾报告（供下次预测前调用）"""
    ledger = load_ledger()
    params = ledger["model_params"]

    report = []
    report.append("=" * 60)
    report.append("📊 世界杯预测引擎 - 自我进化回顾报告")
    report.append("=" * 60)
    report.append(f"总预测次数: {params['total_predictions']}")

    completed = [p for p in ledger["predictions"] if p["actual_result"]]
    pending = [p for p in ledger["predictions"] if not p["actual_result"]]

    if completed:
        report.append(f"已验证预测: {len(completed)}")
        report.append(f"胜平负命中率: {params['correct_result_count']}/{len(completed)} = {params['correct_result_count']/len(completed)*100:.1f}%")
        report.append(f"比分精确命中: {params['correct_score_count']}/{len(completed)}")
        report.append(f"平均比分偏差: {params['avg_score_deviation']:.2f} 球")
        report.append("")

        report.append("--- 已验证预测详情 ---")
        for p in completed:
            pa, pb = p["predicted_score"]["team_a"], p["predicted_score"]["team_b"]
            aa, ab = p["actual_result"]["team_a"], p["actual_result"]["team_b"]
            emoji = "🎯" if pa == aa and pb == ab else ("✅" if p["score"] >= 50 else "❌")
            report.append(f"{emoji} {p['match']}: 预测 {pa}:{pb} | 实际 {aa}:{ab} | 得分 {p['score']}/100")
            if p["reflection"]:
                for item in p["reflection"].get("what_went_wrong", []):
                    report.append(f"   {item}")
                for cause in p["reflection"].get("root_causes", []):
                    report.append(f"   💡 {cause}")
        report.append("")

    if pending:
        report.append("--- 待验证预测 ---")
        for p in pending:
            pa, pb = p["predicted_score"]["team_a"], p["predicted_score"]["team_b"]
            report.append(f"⏳ {p['match']}: 预测 {pa}:{pb} (信心: {p['confidence']}/5)")
        report.append("")

    report.append("--- 当前模型权重（经自我进化调整后）---")
    for dim, weight in params["dimension_weights"].items():
        bar = "█" * int(weight * 100) + "░" * (25 - int(weight * 100))
        report.append(f"  {dim:20s}: {bar} {weight*100:.1f}%")

    if ledger["evolution_insights"]:
        report.append("")
        report.append("--- 最近进化洞察 ---")
        for insight in ledger["evolution_insights"][-3:]:
            report.append(f"📅 {insight['timestamp'][:10]} | {insight['match']} | 得分: {insight['score']}/100")
            for lesson in insight.get("lesson", []):
                report.append(f"   📖 {lesson}")

    report.append("=" * 60)
    return "\n".join(report)

def get_pending_predictions():
    """获取所有待验证的预测（需要用户确认真实结果）"""
    ledger = load_ledger()
    pending = [p for p in ledger["predictions"] if not p["actual_result"]]
    return pending

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("用法:")
        print("  python evolution_ledger.py review          - 查看历史回顾报告")
        print("  python evolution_ledger.py pending         - 查看待验证预测")
        print("  python evolution_ledger.py add <A> <B> <sA> <sB> <pA> <pD> <pB> <conf> <reason>")
        print("  python evolution_ledger.py result <id> <sA> <sB>  - 记录真实结果")
        sys.exit(0)

    action = sys.argv[1]

    if action == "review":
        print(get_review_report())
    elif action == "pending":
        pending = get_pending_predictions()
        if not pending:
            print("🎉 没有待验证的预测！")
        else:
            for p in pending:
                pa, pb = p["predicted_score"]["team_a"], p["predicted_score"]["team_b"]
                print(f"ID:{p['id']} | {p['match']}: 预测 {pa}:{pb} | {p['timestamp'][:10]}")
    elif action == "add" and len(sys.argv) >= 11:
        add_prediction(
            sys.argv[2], sys.argv[3],
            int(sys.argv[4]), int(sys.argv[5]),
            float(sys.argv[6]), float(sys.argv[7]), float(sys.argv[8]),
            int(sys.argv[9]), sys.argv[10]
        )
    elif action == "result" and len(sys.argv) >= 5:
        record_actual_result(int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4]))
    else:
        print("❌ 无效的命令参数")
