class TestAuth:
    def test_login_admin_existe(self, client):
        response = client.post("/api/login", json={
            "email": "admin@colegio.com",
            "password": "test"
        })
        assert response.status_code == 200
        assert response.json()["status"] == "success"

    def test_login_usuario_no_existe(self, client):
        response = client.post("/api/login", json={
            "email": "noexiste@test.com",
            "password": "test"
        })
        assert response.status_code == 401
