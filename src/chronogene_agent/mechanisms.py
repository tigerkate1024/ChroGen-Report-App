
MECHANISM_COLUMNS = [
    "mitochondrial_repair_decline",
    "oxidative_photooxidative_stress",
    "chronic_inflammation_SASP",
    "ECM_collagen_degradation",
    "glycation_metabolic_stress",
    "barrier_resilience_decline",
    "DNA_damage_cellular_senescence",
    "proteostasis_autophagy_decline",
    "oral_microbiome_mucosal_inflammation_axis",
    "circadian_stress_recovery_axis",
]

MECHANISM_LABELS = {
    "mitochondrial_repair_decline": "线粒体修复力下降",
    "oxidative_photooxidative_stress": "氧化/光氧化压力",
    "chronic_inflammation_SASP": "慢性炎症 / SASP",
    "ECM_collagen_degradation": "胶原 ECM 降解",
    "glycation_metabolic_stress": "糖化与代谢压力",
    "barrier_resilience_decline": "屏障韧性不足",
    "DNA_damage_cellular_senescence": "DNA 损伤/细胞衰老",
    "proteostasis_autophagy_decline": "蛋白稳态/自噬下降",
    "oral_microbiome_mucosal_inflammation_axis": "口腔微生态-黏膜炎症轴",
    "circadian_stress_recovery_axis": "节律-压力-恢复轴",
}

MECHANISM_SHORT = {
    "mitochondrial_repair_decline": "Mito",
    "oxidative_photooxidative_stress": "Oxidative",
    "chronic_inflammation_SASP": "Inflammation",
    "ECM_collagen_degradation": "ECM",
    "glycation_metabolic_stress": "Glycation",
    "barrier_resilience_decline": "Barrier",
    "DNA_damage_cellular_senescence": "DNA/Senescence",
    "proteostasis_autophagy_decline": "Proteostasis",
    "oral_microbiome_mucosal_inflammation_axis": "Oral Axis",
    "circadian_stress_recovery_axis": "Recovery",
}

EVIDENCE_RULES = {
    "oxidative_photooxidative_stress": [
        ("face_skin", "pigmentation_uv_index", "面部色素/UV 损伤表型"),
        ("face_skin", "redness_inflammation_index", "红区/炎症视觉信号"),
        ("lifestyle", "uv_exposure_score_0_100", "紫外线暴露"),
        ("lifestyle", "sunscreen_adherence_0_100", "防晒依从性，低分提示风险"),
        ("skin_scrna", "ROS_response_score", "皮肤细胞 ROS response"),
        ("oral_epi", "oxidative_stress_response_score", "口腔上皮 oxidative stress response"),
        ("genome", "NRF2_KEAP1_antioxidant_response_risk", "抗氧化应答遗传风险"),
    ],
    "chronic_inflammation_SASP": [
        ("face_skin", "redness_inflammation_index", "红区/敏感/炎症视觉信号"),
        ("skin_scrna", "NFkB_TNF_IL1_inflammation_score", "NF-kB / TNF / IL-1 炎症通路"),
        ("skin_scrna", "SASP_score", "SASP signature"),
        ("oral_epi", "IL1B_IL6_TNF_axis_score", "口腔上皮炎症轴"),
        ("oral_microbiome", "oral_dysbiosis_index", "口腔菌群失衡"),
        ("lifestyle", "stress_score_0_100", "压力暴露"),
        ("lifestyle", "smoking_status", "吸烟状态"),
    ],
    "ECM_collagen_degradation": [
        ("face_skin", "wrinkle_depth_index", "皱纹深度"),
        ("face_skin", "elasticity_loss_proxy", "弹性下降 proxy"),
        ("face_skin", "facial_volume_loss_proxy", "面部容积流失 proxy"),
        ("skin_scrna", "MMP_ECM_degradation_score", "MMP / ECM degradation"),
        ("skin_scrna", "collagen_synthesis_score", "胶原合成能力，低分提示风险"),
        ("genome", "COL1A1_ELN_ECM_remodeling_risk", "胶原/弹性蛋白遗传风险"),
    ],
    "glycation_metabolic_stress": [
        ("face_skin", "texture_roughness_index", "粗糙/暗沉/质地 proxy"),
        ("lifestyle", "added_sugar_score_0_100", "添加糖摄入"),
        ("participants", "BMI", "BMI / 代谢压力 proxy"),
        ("skin_scrna", "AGE_RAGE_glycation_score", "AGE-RAGE / glycation"),
        ("genome", "AGE_RAGE_glycation_risk", "糖化相关遗传风险"),
    ],
    "barrier_resilience_decline": [
        ("face_skin", "barrier_dryness_visual_score", "干燥/屏障视觉评分"),
        ("face_skin", "texture_roughness_index", "粗糙度"),
        ("lifestyle", "skincare_consistency_0_100", "护肤一致性，低分提示风险"),
        ("skin_scrna", "lipid_barrier_ceramide_score", "脂质/神经酰胺 pathway，低分提示风险"),
        ("genome", "FLG_ceramide_barrier_risk", "FLG / ceramide 屏障遗传风险"),
    ],
    "mitochondrial_repair_decline": [
        ("lifestyle", "sleep_hours", "睡眠时长，低值提示恢复不足"),
        ("lifestyle", "exercise_minutes_per_week", "运动量，低值提示线粒体刺激不足"),
        ("lifestyle", "stress_score_0_100", "压力暴露"),
        ("skin_scrna", "OXPHOS_mitochondrial_score", "OXPHOS / mitochondrial pathway，低分提示风险"),
        ("genome", "mtDNA_OXPHOS_mitochondrial_risk", "线粒体/OXPHOS 遗传风险"),
    ],
    "DNA_damage_cellular_senescence": [
        ("lifestyle", "uv_exposure_score_0_100", "紫外线暴露"),
        ("face_skin", "pigmentation_uv_index", "光损伤表型"),
        ("skin_scrna", "DNA_repair_p53_p21_score", "p53 / p21 / DNA repair signature"),
        ("skin_scrna", "SASP_score", "SASP 与细胞衰老关联"),
        ("genome", "TP53_DNA_repair_senescence_risk", "DNA repair / senescence 遗传风险"),
    ],
    "proteostasis_autophagy_decline": [
        ("skin_scrna", "autophagy_lysosome_score", "自噬/溶酶体 pathway，低分提示风险"),
        ("skin_scrna", "OXPHOS_mitochondrial_score", "线粒体压力与蛋白稳态关联"),
        ("lifestyle", "sleep_hours", "睡眠恢复不足"),
        ("lifestyle", "stress_score_0_100", "慢性压力"),
    ],
    "oral_microbiome_mucosal_inflammation_axis": [
        ("oral_microbiome", "oral_dysbiosis_index", "口腔菌群失衡"),
        ("oral_microbiome", "LPS_biosynthesis_functional_score", "LPS-like inflammatory functional score"),
        ("oral_microbiome", "alpha_diversity_shannon", "alpha diversity，低值提示失衡"),
        ("oral_epi", "CXCL8_neutrophil_recruitment_score", "中性粒细胞募集 signature"),
        ("oral_epi", "epithelial_barrier_tight_junction_score", "上皮 tight junction，低分提示屏障压力"),
    ],
    "circadian_stress_recovery_axis": [
        ("lifestyle", "sleep_hours", "睡眠时长"),
        ("lifestyle", "stress_score_0_100", "压力评分"),
        ("lifestyle", "exercise_minutes_per_week", "运动恢复节律"),
        ("skin_scrna", "SASP_score", "压力-炎症关联"),
        ("oral_epi", "wound_healing_epithelial_turnover_score", "黏膜修复/turnover signature"),
    ],
}

FOLLOW_UP_METRICS = {
    "oxidative_photooxidative_stress": ["面部色素/UV index", "皮肤 ROS pathway", "口腔上皮 oxidative stress", "防晒依从性"],
    "chronic_inflammation_SASP": ["红区/敏感指数", "NF-kB/TNF/IL-1", "SASP score", "口腔炎症轴"],
    "ECM_collagen_degradation": ["皱纹深度", "弹性下降 proxy", "MMP/ECM score", "collagen synthesis"],
    "glycation_metabolic_stress": ["添加糖评分", "AGE-RAGE score", "质地粗糙度", "BMI / 代谢 proxy"],
    "barrier_resilience_decline": ["干燥/屏障评分", "lipid/ceramide pathway", "护肤一致性", "TEWL/水分 if available"],
    "mitochondrial_repair_decline": ["睡眠时长", "运动量", "OXPHOS score", "主观精力"],
    "DNA_damage_cellular_senescence": ["UV 暴露", "DNA repair/p53/p21", "SASP score", "pigmentation index"],
    "proteostasis_autophagy_decline": ["autophagy/lysosome score", "睡眠", "压力", "恢复感"],
    "oral_microbiome_mucosal_inflammation_axis": ["oral dysbiosis", "LPS function", "CXCL8 score", "alpha diversity"],
    "circadian_stress_recovery_axis": ["睡眠", "压力", "运动恢复", "HRV if available"],
}
