from app.services.memory import score_memory


def test_memory_retriever_prioritizes_important_memory():
    high = score_memory(
        content="王一诺迟到了并向林见川求助。",
        importance=5,
        created_day=1,
        created_minute=480,
        current_day=1,
        current_minute=540,
        query_terms=["林见川", "求助"],
    )
    low = score_memory(
        content="王一诺路过食堂。",
        importance=1,
        created_day=1,
        created_minute=480,
        current_day=1,
        current_minute=540,
        query_terms=["林见川", "求助"],
    )

    assert high > low


def test_memory_retriever_prioritizes_relevance():
    relevant = score_memory("周岚在图书馆捡到校园卡。", 2, 1, 600, 1, 660, ["图书馆", "校园卡"])
    irrelevant = score_memory("陈念在食堂排队。", 2, 1, 600, 1, 660, ["图书馆", "校园卡"])

    assert relevant > irrelevant
