# Movernos en el laberito

1. Definir 2 estados
* Estado 1:
  * El robot debe avanzar hacia adelante si el sensor de distancia1
    marca una distancia mayor a (baldoza/2) -> 0.06
  * Sino el robot debe pasar al estado 2
* Estado 2:
  * El robot debe rotar 90 grados (Rotar debe ser no bloqueante)
  * Una vez terminada la rotacion -> veo si la distancia1 es mayor (baldoza/2)
    * Si la distancia es mayor vuelvo al estado 1
    * sino vuelvo a rotar 90 grados.
