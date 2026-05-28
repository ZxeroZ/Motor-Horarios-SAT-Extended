class TestSchedule:
    def test_get_horario_final_vacio(self, client):
        response = client.get("/api/horario-final")
        assert response.status_code == 200
        assert response.json() == []

    def test_cargar_horario_vacio(self, client):
        response = client.get("/api/cargar-horario")
        assert response.status_code == 200
        assert response.json()["status"] == "empty"

    def test_generar_horario_validacion_falla(self, client):
        response = client.post("/api/generar-horario")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "error"
        assert "errores" in data
