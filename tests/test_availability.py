class TestAvailability:
    def test_create_disponibilidad(self, client, seed_infra):
        response = client.post("/api/profesor-disponibilidad", json={
            "id_profesor": seed_infra["profesor"].id_profesor,
            "id_dia": seed_infra["dia"].id_dia,
            "id_turno": seed_infra["turno"].id_turno,
            "id_sede": seed_infra["sede"].id_sede,
            "nro_bloque": 1
        })
        assert response.status_code == 201

    def test_create_disponibilidad_profesor_no_existe(self, client, seed_infra):
        response = client.post("/api/profesor-disponibilidad", json={
            "id_profesor": 9999,
            "id_dia": seed_infra["dia"].id_dia,
            "id_turno": seed_infra["turno"].id_turno,
            "id_sede": seed_infra["sede"].id_sede,
            "nro_bloque": 1
        })
        assert response.status_code == 400

    def test_create_preferencia(self, client, seed_infra):
        response = client.post("/api/profesor-preferencia", json={
            "id_profesor": seed_infra["profesor"].id_profesor,
            "id_dia": seed_infra["dia"].id_dia,
            "id_turno": seed_infra["turno"].id_turno,
            "id_sede": seed_infra["sede"].id_sede,
            "nro_bloque": 2
        })
        assert response.status_code == 201

    def test_create_preferencia_sede_no_existe(self, client, seed_infra):
        response = client.post("/api/profesor-preferencia", json={
            "id_profesor": seed_infra["profesor"].id_profesor,
            "id_dia": seed_infra["dia"].id_dia,
            "id_turno": seed_infra["turno"].id_turno,
            "id_sede": 9999,
            "nro_bloque": 1
        })
        assert response.status_code == 400

    def test_delete_disponibilidad(self, client, seed_infra):
        disp = client.post("/api/profesor-disponibilidad", json={
            "id_profesor": seed_infra["profesor"].id_profesor,
            "id_dia": seed_infra["dia"].id_dia,
            "id_turno": seed_infra["turno"].id_turno,
            "id_sede": seed_infra["sede"].id_sede,
            "nro_bloque": 3
        }).json()
        response = client.delete(f"/api/profesor-disponibilidad/{disp['id_disponibilidad']}")
        assert response.status_code == 200
