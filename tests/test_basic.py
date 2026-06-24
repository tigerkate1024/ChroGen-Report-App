
from chronogene_agent.data_loader import load_tables
from chronogene_agent.model import get_target_scores
from chronogene_agent.report import top_mechanisms

def test_load_data():
    data = load_tables("data")
    assert "participants" in data.tables
    assert "CG0039" in set(data.tables["participants"]["subject_id"])

def test_target_scores():
    data = load_tables("data")
    scores = get_target_scores(data.tables, "CG0039")
    assert scores["oxidative_photooxidative_stress"] == 64.5
    top = top_mechanisms(scores, 1)
    assert top[0][0] == "oxidative_photooxidative_stress"
