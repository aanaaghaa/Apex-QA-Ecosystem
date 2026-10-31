class EnvironmentConfig:
    # Front-end UI web interface port mapping
    BASE_UI_URL = "http://localhost:4200"
    
    # Direct backend database API gateway engine endpoint
    # This is where our API-UI Hybrid Resiliency Loop dispatches its POST payloads
    BASE_API_URL = "http://localhost:8080/api" 
