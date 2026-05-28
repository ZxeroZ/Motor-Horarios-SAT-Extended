class TestInfra:
    def test_get_colegio(self, client):
        response = client.get("/api/colegio")
        assert response.status_code == 200
        assert isinstance(response.json(), list)

    def test_create_sede(self, client, seed_infra):
        response = client.post("/api/sedes", json={
            "nombre_sede": "Sede Nueva",
            "id_colegio": seed_infra["colegio"].id_colegio
        })
        assert response.status_code == 201
        data = response.json()
        assert data["nombre_sede"] == "Sede Nueva"

    def test_create_sede_nombre_vacio(self, client):
        response = client.post("/api/sedes", json={"nombre_sede": ""})
        assert response.status_code == 422

    def test_create_grado(self, client):
        response = client.post("/api/grados", json={"numero": 5})
        assert response.status_code == 201
        assert response.json()["numero"] == 5

    def test_create_grado_numero_invalido(self, client):
        response = client.post("/api/grados", json={"numero": 0})
        assert response.status_code == 422

    def test_create_dia(self, client):
        response = client.post("/api/dias", json={"nombre_dia": "Martes", "orden": 2})
        assert response.status_code == 201

    def test_create_turno(self, client):
        response = client.post("/api/turnos", json={"nombre": "Tarde"})
        assert response.status_code == 201

    def test_create_grado_dia_config(self, client, seed_infra):
        response = client.post("/api/grado-dia-config", json={
            "id_grado": seed_infra["grado"].id_grado,
            "id_dia": seed_infra["dia"].id_dia,
            "bloques_dia": 6
        })
        assert response.status_code == 201

    def test_create_grado_dia_config_bloques_invalidos(self, client, seed_infra):
        response = client.post("/api/grado-dia-config", json={
            "id_grado": seed_infra["grado"].id_grado,
            "id_dia": seed_infra["dia"].id_dia,
            "bloques_dia": 0
        })
        assert response.status_code == 422

    def test_delete_grado_dia_config(self, client, seed_infra):
        create = client.post("/api/grado-dia-config", json={
            "id_grado": seed_infra["grado"].id_grado,
            "id_dia": seed_infra["dia"].id_dia,
            "bloques_dia": 6
        })
        config_id = create.json()["id_config"]
        response = client.delete(f"/api/grado-dia-config/{config_id}")
        assert response.status_code == 200

    def test_update_colegio(self, client, seed_infra):
        response = client.put(f"/api/colegio/{seed_infra['colegio'].id_colegio}", json={
            "nombre_colegio": "Colegio Actualizado"
        })
        assert response.status_code == 200
        assert response.json()["nombre_colegio"] == "Colegio Actualizado"
