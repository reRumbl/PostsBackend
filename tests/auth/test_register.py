import pytest
from httpx import AsyncClient
from tests.conftest import test_async_client


class TestRegister:
    @pytest.mark.asyncio
    async def test_register(self, test_async_client: AsyncClient):
        response = await test_async_client.post(
            '/api/auth/register',
            json={
                'email': 'test@email.net',
                'username': 'TestUser',
                'password': 'testpassword123',
                'confirm_password': 'testpassword123'
            }
        )
        print(response.json() if response.status_code != 200 else None)
        assert response.status_code == 200
        assert response.json()['email'] == 'test@email.net'
        assert response.json()['username'] == 'TestUser'
