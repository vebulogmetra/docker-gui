"""
Мок данные для тестирования Docker GUI
"""

# Мок данные для контейнеров
MOCK_CONTAINERS = [
    {
        "id": "test_container_1",
        "name": "test_container_1",
        "status": "running",
        "image": "test_image:latest",
        "ports": {"80/tcp": [{"HostIp": "0.0.0.0", "HostPort": "8080"}]},
        "labels": {"com.example.some-label": "some-value"},
        "created": "2024-01-01T00:00:00Z",
        "size": 1024*1024*50,  # 50MB
        "mounts": [],
        "network_settings": {
            "networks": {
                "bridge": {
                    "ip_address": "172.17.0.2",
                    "gateway": "172.17.0.1"
                }
            }
        }
    },
    {
        "id": "test_container_2",
        "name": "test_container_2", 
        "status": "exited",
        "image": "test_image:latest",
        "ports": {},
        "labels": {},
        "created": "2024-01-01T01:00:00Z",
        "size": 1024*1024*25,  # 25MB
        "mounts": [],
        "network_settings": {
            "networks": {}
        }
    },
    {
        "id": "test_container_3",
        "name": "test_container_3",
        "status": "paused",
        "image": "test_image2:latest",
        "ports": {},
        "labels": {},
        "created": "2024-01-01T02:00:00Z",
        "size": 1024*1024*75,  # 75MB
        "mounts": [],
        "network_settings": {
            "networks": {}
        }
    }
]

# Мок данные для образов
MOCK_IMAGES = [
    {
        "id": "test_image_1",
        "tags": ["test_image:latest", "test_image:v1.0"],
        "size": 1024*1024*100,  # 100MB
        "created": "2024-01-01T00:00:00Z",
        "labels": {"com.example.version": "1.0"},
        "architecture": "amd64",
        "os": "linux",
        "digest": "sha256:test_digest_1"
    },
    {
        "id": "test_image_2",
        "tags": ["test_image2:latest"],
        "size": 1024*1024*50,  # 50MB
        "created": "2024-01-01T01:00:00Z",
        "labels": {},
        "architecture": "amd64",
        "os": "linux",
        "digest": "sha256:test_digest_2"
    },
    {
        "id": "test_image_3",
        "tags": ["test_image3:latest", "test_image3:v2.0"],
        "size": 1024*1024*200,  # 200MB
        "created": "2024-01-01T02:00:00Z",
        "labels": {"com.example.version": "2.0"},
        "architecture": "amd64",
        "os": "linux",
        "digest": "sha256:test_digest_3"
    }
]

# Мок данные для сетей
MOCK_NETWORKS = [
    {
        "id": "test_network_1",
        "name": "bridge",
        "driver": "bridge",
        "scope": "local",
        "ipam": {
            "config": [
                {
                    "subnet": "172.17.0.0/16",
                    "gateway": "172.17.0.1"
                }
            ]
        },
        "internal": False,
        "attachable": False,
        "ingress": False,
        "enable_ipv6": False,
        "options": {}
    },
    {
        "id": "test_network_2",
        "name": "test_network",
        "driver": "bridge",
        "scope": "local",
        "ipam": {
            "config": [
                {
                    "subnet": "172.18.0.0/16",
                    "gateway": "172.18.0.1"
                }
            ]
        },
        "internal": False,
        "attachable": True,
        "ingress": False,
        "enable_ipv6": False,
        "options": {}
    },
    {
        "id": "test_network_3",
        "name": "host",
        "driver": "host",
        "scope": "local",
        "ipam": {
            "config": []
        },
        "internal": False,
        "attachable": False,
        "ingress": False,
        "enable_ipv6": False,
        "options": {}
    }
]

# Мок данные для томов
MOCK_VOLUMES = [
    {
        "id": "test_volume_1",
        "name": "test_volume_1",
        "driver": "local",
        "mountpoint": "/var/lib/docker/volumes/test_volume_1/_data",
        "created": "2024-01-01T00:00:00Z",
        "status": {},
        "labels": {"com.example.volume": "data"},
        "scope": "local",
        "options": {}
    },
    {
        "id": "test_volume_2",
        "name": "test_volume_2",
        "driver": "local",
        "mountpoint": "/var/lib/docker/volumes/test_volume_2/_data",
        "created": "2024-01-01T01:00:00Z",
        "status": {},
        "labels": {},
        "scope": "local",
        "options": {}
    },
    {
        "id": "test_volume_3",
        "name": "test_volume_3",
        "driver": "local",
        "mountpoint": "/var/lib/docker/volumes/test_volume_3/_data",
        "created": "2024-01-01T02:00:00Z",
        "status": {},
        "labels": {"com.example.volume": "cache"},
        "scope": "local",
        "options": {}
    }
]

# Мок данные для статистики
MOCK_STATISTICS = {
    "containers": {
        "total": 3,
        "running": 1,
        "exited": 1,
        "paused": 1
    },
    "images": {
        "total": 3,
        "size": 1024*1024*350  # 350MB total
    },
    "networks": {
        "total": 3,
        "bridge": 1,
        "host": 1,
        "custom": 1
    },
    "volumes": {
        "total": 3,
        "size": 1024*1024*500  # 500MB total
    }
}

# Мок данные для операций очистки
MOCK_PRUNE_RESULTS = {
    "containers": {
        "ContainersDeleted": ["test_container_2"],
        "SpaceReclaimed": 1024*1024*25  # 25MB
    },
    "images": {
        "ImagesDeleted": ["test_image_2"],
        "SpaceReclaimed": 1024*1024*50  # 50MB
    },
    "networks": {
        "NetworksDeleted": ["test_network_2"]
    },
    "volumes": {
        "VolumesDeleted": ["test_volume_2"],
        "SpaceReclaimed": 1024*1024*100  # 100MB
    }
}

# Мок данные для ошибок
MOCK_ERRORS = {
    "container_not_found": "Error response from daemon: No such container: invalid_container",
    "image_not_found": "Error response from daemon: No such image: invalid_image",
    "network_not_found": "Error response from daemon: No such network: invalid_network",
    "volume_not_found": "Error response from daemon: No such volume: invalid_volume",
    "permission_denied": "Error response from daemon: permission denied",
    "connection_failed": "Error response from daemon: dial unix /var/run/docker.sock: connect: connection refused"
}

# Мок данные для событий
MOCK_EVENTS = [
    {
        "type": "container",
        "action": "start",
        "actor": {
            "id": "test_container_1",
            "attributes": {
                "name": "test_container_1",
                "image": "test_image:latest"
            }
        },
        "time": "2024-01-01T00:00:00Z"
    },
    {
        "type": "container",
        "action": "stop",
        "actor": {
            "id": "test_container_2",
            "attributes": {
                "name": "test_container_2",
                "image": "test_image:latest"
            }
        },
        "time": "2024-01-01T01:00:00Z"
    },
    {
        "type": "image",
        "action": "pull",
        "actor": {
            "id": "test_image_1",
            "attributes": {
                "name": "test_image:latest"
            }
        },
        "time": "2024-01-01T02:00:00Z"
    }
]

# Мок данные для настроек
MOCK_SETTINGS = {
    "auto_refresh": True,
    "refresh_interval": 30,
    "theme": "light",
    "language": "ru",
    "window_size": {
        "width": 1024,
        "height": 768
    },
    "window_position": {
        "x": 100,
        "y": 100
    },
    "columns": {
        "containers": ["name", "status", "image", "ports"],
        "images": ["tags", "size", "created"],
        "networks": ["name", "driver", "scope"],
        "volumes": ["name", "driver", "mountpoint"]
    },
    "sorting": {
        "containers": {"column": "name", "direction": "asc"},
        "images": {"column": "size", "direction": "desc"},
        "networks": {"column": "name", "direction": "asc"},
        "volumes": {"column": "name", "direction": "asc"}
    }
}

# Мок данные для логов
MOCK_LOGS = {
    "test_container_1": [
        "2024-01-01T00:00:01Z INFO: Container started",
        "2024-01-01T00:00:02Z INFO: Application initialized",
        "2024-01-01T00:00:03Z INFO: Server listening on port 80"
    ],
    "test_container_2": [
        "2024-01-01T01:00:01Z INFO: Container started",
        "2024-01-01T01:00:02Z ERROR: Application failed to start",
        "2024-01-01T01:00:03Z INFO: Container stopped"
    ]
}

# Мок данные для информации о системе
MOCK_SYSTEM_INFO = {
    "docker_version": "24.0.7",
    "api_version": "1.43",
    "go_version": "go1.20.10",
    "os": "linux",
    "arch": "x86_64",
    "kernel_version": "6.8.0-64-generic",
    "operating_system": "Ubuntu 24.04.1 LTS",
    "total_memory": 8589934592,  # 8GB
    "available_memory": 4294967296,  # 4GB
    "total_disk": 107374182400,  # 100GB
    "available_disk": 53687091200,  # 50GB
    "cpus": 4,
    "containers": 3,
    "images": 3,
    "driver": "overlay2",
    "driver_status": [
        ["Backing Filesystem", "extfs"],
        ["Supports d_type", "true"],
        ["Native Overlay Diff", "true"]
    ],
    "plugins": {
        "Volume": ["local"],
        "Network": ["bridge", "host", "null", "overlay"],
        "Authorization": null,
        "Log": ["awslogs", "fluentd", "gcplogs", "gelf", "journald", "json-file", "local", "logentries", "splunk", "syslog"]
    }
} 