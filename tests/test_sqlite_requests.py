from datetime import datetime, timedelta

import pytest

import sqlite.requests as rq

@pytest.mark.asyncio
async def test_user_operations(session):
    user_id = 123
    assert await rq.check_user(user_id, session) is False
    await rq.add_user(user_id=user_id, group_id=1, session=session)
    assert await rq.check_user(user_id, session) is True
    group_id = await rq.get_group_id(user_id, session)
    assert group_id == 1

@pytest.mark.asyncio
async def test_remind_crud(session):
    user_id = 321
    await rq.add_user(user_id=user_id, group_id=10, session=session)
    now = datetime.now()
    await rq.set_remind(tg_id=user_id, data=now, text="test", hours=1, session=session)
    reminders = list(await rq.get_reminders(session, user_id))
    assert len(reminders) == 1
    remind = reminders[0]
    got = await rq.get_one_remind(remind.id, session)
    assert got.text == "test"
    await rq.delete_remind(remind.id, session)
    reminders_after = list(await rq.get_reminders(session, user_id))
    assert reminders_after == []

@pytest.mark.asyncio
async def test_check_remind_sql_calls_send(monkeypatch, session):
    calls = {}
    async def fake_send_reminders(bot, ready, sess):
        calls['called'] = True
    monkeypatch.setattr(rq, 'send_reminders', fake_send_reminders)
    await rq.add_user(user_id=1, group_id=1, session=session)
    past = datetime.now() - timedelta(hours=1)
    await rq.set_remind(tg_id=1, data=past, text="r", hours=1, session=session)
    class DummyBot:
        pass
    await rq.check_remind_sql(DummyBot(), session)
    assert calls.get('called') is True
