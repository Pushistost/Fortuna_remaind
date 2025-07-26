import pytest
from types import SimpleNamespace

from tgbot.handlers import user as user_handlers
from tgbot.misc.states import UserForm

class FakeMessage:
    def __init__(self, user_id):
        self.from_user = SimpleNamespace(id=user_id)
        self.answers = []

    async def answer(self, text, **kwargs):
        self.answers.append(text)

class FakeState:
    def __init__(self):
        self.state = None

    async def set_state(self, s):
        self.state = s

    async def clear(self):
        self.state = None

@pytest.mark.asyncio
async def test_user_start_new_user():
    msg = FakeMessage(1)
    await user_handlers.user_start(msg, new_user=True)
    assert any("Отправьте сюда id группы" in a for a in msg.answers)

@pytest.mark.asyncio
async def test_add_group_id_valid(monkeypatch, session):
    calls = {}
    async def fake_add_user(user_id, group_id, session):
        calls['data'] = (user_id, group_id)
    monkeypatch.setattr(user_handlers, 'add_user', fake_add_user)
    state = FakeState()
    msg = FakeMessage(5)
    await user_handlers.add_group_id(msg, '10', state, session)
    assert calls['data'] == (5, 10)
    assert state.state is None
    assert any("сохранен" in a for a in msg.answers)

@pytest.mark.asyncio
async def test_add_group_id_invalid(monkeypatch, session):
    monkeypatch.setattr(user_handlers, 'add_user', lambda *a, **k: None)
    state = FakeState()
    msg = FakeMessage(5)
    await user_handlers.add_group_id(msg, 'bad', state, session)
    assert any("Неверный ввод" in a for a in msg.answers)
