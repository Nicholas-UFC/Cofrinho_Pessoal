flowchart TD
    %% Estilos
    classDef default fill:#1e1e1e,stroke:#333,color:#d4d4d4;
    classDef dockerNode fill:#161b22,stroke:#0db7ed,stroke-width:2px,color:#fff,stroke-dasharray: 5 5;
    classDef nginxNode fill:#009639,stroke:#006629,stroke-width:2px,color:#fff;
    classDef djangoNode fill:#092e20,stroke:#44b78b,stroke-width:2px,color:#fff;
    classDef reactNode fill:#20232a,stroke:#61dafb,stroke-width:2px,color:#fff;
    classDef wahaNode fill:#128c7e,stroke:#25d366,stroke-width:2px,color:#fff;
    classDef geminiNode fill:#1a2736,stroke:#4285f4,stroke-width:2px,color:#fff;
    classDef dbNode fill:#2d333b,stroke:#3498db,stroke-width:2px,color:#fff;
    classDef uiNode fill:#282c34,stroke:#e06c75,stroke-width:2px,color:#abb2bf;

    %% 1. CAMADA DE CLIENTES (EXTERNO)
    subgraph Clientes ["          📱 Clientes Externos (Ponto de Partida)          "]
        direction LR
        WPP["🌐 Fonte Externa\nWhatsApp Group"]:::uiNode
        
        space_h1[ ] ~~~ space_h2[ ]
        style space_h1 fill:none,stroke:none
        style space_h2 fill:none,stroke:none

        RN["🌐 Fonte Externa\nReact Native App"]:::uiNode
        Browser["🌐 Fonte Externa\nWeb Browser"]:::uiNode
        
        WPP ~~~ space_h1 ~~~ RN ~~~ space_h2 ~~~ Browser
    end

    subgraph Docker [" 🐳 Infraestrutura Docker (docker-compose) "]
        direction TB

        respiro_t1[ ]
        respiro_t2[ ]
        style respiro_t1 fill:none,stroke:none
        style respiro_t2 fill:none,stroke:none

        subgraph CamadaEntrada ["Rede de Entrada"]
            direction LR
            style CamadaEntrada fill:none,stroke:none
            WAHA["📦 Container\nWAHA Gateway"]:::wahaNode
            Nginx["📦 Container\nNginx Reverse Proxy"]:::nginxNode
        end
        
        respiro_t1 --- WAHA
        respiro_t2 --- Nginx

        subgraph Interno [" 🔒 Núcleo de Processamento "]
            direction LR
            React["📦 Container\nReact Web"]:::reactNode
            Django["📦 Container\nDjango REST"]:::djangoNode
            Gemini["🌐 Fonte Externa\nGemini AI API"]:::geminiNode
        end

        SQLite["📦 Container\nSQLite File"]:::dbNode
    end

    %% FLUXOS DE DADOS (CONEXÕES CORRIGIDAS)
    %% Caminho do WhatsApp
    WPP ===> WAHA
    WAHA ===> Django

    %% Caminho dos outros Clientes
    RN & Browser ----> Nginx
    Nginx ----> React
    Nginx ----> Django
    
    %% Processamento Interno
    Django <----> Gemini
    Django ----> SQLite

    class Docker dockerNode;