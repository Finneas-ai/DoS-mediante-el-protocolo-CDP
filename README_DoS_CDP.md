# 📡 DoS mediante el protocolo CDP

> **Laboratorio de Seguridad de Redes — ITLA**  
> Autor: Mario Alejandro de León Peña | Matrícula: 2025-0682  
> Materia: Seguridad Informática — Seguridad de Redes  
> Profesor: Jonathan Esteban Rondon Corniel

[![Python](https://img.shields.io/badge/Python-3.x-blue?logo=python)](https://www.python.org/)
[![Scapy](https://img.shields.io/badge/Scapy-required-orange)](https://scapy.net/)
[![License](https://img.shields.io/badge/License-Educational-green)]()
[![Video Demo](https://img.shields.io/badge/Demo-YouTube-red?logo=youtube)](https://youtu.be/88sIQspK2iQ)

---

## 📋 Descripción

Este laboratorio demuestra cómo un atacante puede afectar la disponibilidad y el rendimiento de **switches y routers Cisco** mediante el envío masivo de paquetes **CDP (Cisco Discovery Protocol)** falsificados. Este tipo de tráfico puede saturar la memoria y el procesamiento del dispositivo, provocando degradación del servicio e incluso una **denegación de servicio (DoS)**.

---

## 🎯 Objetivos

### Objetivo del Laboratorio
Evidenciar el impacto del tráfico CDP malicioso sobre los recursos internos de dispositivos Cisco, especialmente en memoria y procesamiento, provocando degradación del servicio de administración.

### Objetivo del Script
Incrementar artificialmente la cantidad de **vecinos CDP detectados** por el equipo objetivo, obligándolo a procesar y almacenar grandes cantidades de información hasta saturar sus recursos.

---

## ⚙️ Requisitos

- Python 3.x
- Scapy (`pip install scapy`)
- Permisos root
- Interfaz conectada al segmento con switches Cisco con CDP activo

---

## 🚀 Uso

```bash
sudo python3 CDP.py <iface> [-c <count>] [-d <delay>]
```

### Parámetros

| Parámetro | Descripción | Obligatorio |
|-----------|-------------|:-----------:|
| `iface` | Interfaz de red del atacante (ej. `eth0`) | ✅ |
| `-c` / `--count` | Número de paquetes a enviar (`0` = infinito) | ❌ |
| `-d` / `--delay` | Retardo en segundos entre paquetes | ❌ |

### Ejemplo

```bash
sudo python3 CDP.py ens3 -c 10000 -d 0.001
```

---

## 🔄 Flujo de Ejecución

```
1. Se genera una dirección MAC de origen aleatoria por cada paquete
2. Se construye un frame Ethernet con destino multicast CDP (01:00:0c:cc:cc:cc)
3. El payload incluye encabezado LLC/SNAP estándar de Cisco y un TLV Device-ID aleatorio
4. El paquete se inyecta directamente en la interfaz de red con sendp()
5. Al recibir miles de entradas nuevas por segundo, el switch no puede gestionar su tabla CDP y degrada su rendimiento
```

---

---

## 🛡️ Contramedidas

| Medida | Comando / Acción | Efecto |
|--------|-----------------|--------|
| Deshabilitar CDP globalmente | `no cdp run` | Elimina el vector de ataque completamente |

---

## 🎬 Demo

📺 [Ver video de demostración](https://youtu.be/88sIQspK2iQ)

---

## ⚠️ Aviso Legal

> Este proyecto es exclusivamente con fines **educativos** en un entorno controlado de laboratorio. El uso de estas técnicas fuera de entornos autorizados es ilegal y éticamente incorrecto.
