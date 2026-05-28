class TestAcademic:
    def test_create_area(self, client):
        response = client.post("/api/areas", json={"nombre": "Ciencias", "max_horas_dia": 3})
        assert response.status_code == 201
        assert response.json()["nombre"] == "Ciencias"

    def test_create_area_nombre_vacio(self, client):
        response = client.post("/api/areas", json={"nombre": ""})
        assert response.status_code == 422

    def test_create_area_max_horas_invalido(self, client):
        response = client.post("/api/areas", json={"nombre": "Historia", "max_horas_dia": 0})
        assert response.status_code == 422

    def test_create_curso_con_area_valida(self, client, seed_infra):
        response = client.post("/api/cursos", json={
            "nombre_curso": "Geometría",
            "id_area": seed_infra["area"].id_area
        })
        assert response.status_code == 201

    def test_create_curso_area_no_existe(self, client):
        response = client.post("/api/cursos", json={
            "nombre_curso": "Física",
            "id_area": 9999
        })
        assert response.status_code == 400
        assert "no existe" in response.json()["detail"]

    def test_create_profesor(self, client):
        response = client.post("/api/profesores", json={"nombre_profesor": "María García"})
        assert response.status_code == 201

    def test_create_profesor_nombre_vacio(self, client):
        response = client.post("/api/profesores", json={"nombre_profesor": ""})
        assert response.status_code == 422

    def test_create_seccion(self, client, seed_infra):
        response = client.post("/api/secciones", json={
            "id_sede": seed_infra["sede"].id_sede,
            "id_grado": seed_infra["grado"].id_grado,
            "nombre": "A"
        })
        assert response.status_code == 201

    def test_create_seccion_sede_no_existe(self, client, seed_infra):
        response = client.post("/api/secciones", json={
            "id_sede": 9999,
            "id_grado": seed_infra["grado"].id_grado,
            "nombre": "B"
        })
        assert response.status_code == 400

    def test_create_plan_estudio(self, client, seed_infra):
        response = client.post("/api/planes", json={
            "id_grado": seed_infra["grado"].id_grado,
            "id_curso": seed_infra["curso"].id_curso,
            "horas_semanales": 5
        })
        assert response.status_code == 201

    def test_create_plan_horas_invalidas(self, client, seed_infra):
        response = client.post("/api/planes", json={
            "id_grado": seed_infra["grado"].id_grado,
            "id_curso": seed_infra["curso"].id_curso,
            "horas_semanales": 0
        })
        assert response.status_code == 422

    def test_create_profesor_curso(self, client, seed_infra):
        response = client.post("/api/profesor-curso", json={
            "id_profesor": seed_infra["profesor"].id_profesor,
            "id_curso": seed_infra["curso"].id_curso
        })
        assert response.status_code == 201

    def test_create_profesor_curso_duplicado(self, client, seed_infra):
        client.post("/api/profesor-curso", json={
            "id_profesor": seed_infra["profesor"].id_profesor,
            "id_curso": seed_infra["curso"].id_curso
        })
        response = client.post("/api/profesor-curso", json={
            "id_profesor": seed_infra["profesor"].id_profesor,
            "id_curso": seed_infra["curso"].id_curso
        })
        assert response.status_code == 409
        assert "ya tiene asignado" in response.json()["detail"]

    def test_create_tutoria(self, client, seed_infra):
        sec = client.post("/api/secciones", json={
            "id_sede": seed_infra["sede"].id_sede,
            "id_grado": seed_infra["grado"].id_grado,
            "nombre": "C"
        }).json()

        response = client.post("/api/tutorias", json={
            "id_seccion": sec["id_seccion"],
            "id_profesor": seed_infra["profesor"].id_profesor
        })
        assert response.status_code == 201

    def test_create_tutoria_duplicada_misma_seccion(self, client, seed_infra):
        sec = client.post("/api/secciones", json={
            "id_sede": seed_infra["sede"].id_sede,
            "id_grado": seed_infra["grado"].id_grado,
            "nombre": "D"
        }).json()

        client.post("/api/tutorias", json={
            "id_seccion": sec["id_seccion"],
            "id_profesor": seed_infra["profesor"].id_profesor
        })
        response = client.post("/api/tutorias", json={
            "id_seccion": sec["id_seccion"],
            "id_profesor": seed_infra["profesor"].id_profesor
        })
        assert response.status_code == 409

    def test_delete_curso(self, client, seed_infra):
        curso = client.post("/api/cursos", json={
            "nombre_curso": "Para Borrar",
            "id_area": seed_infra["area"].id_area
        }).json()
        response = client.delete(f"/api/cursos/{curso['id_curso']}")
        assert response.status_code == 200
