#!/usr/bin/env python3
import http.server
import socketserver
import json
import urllib.parse
import os
from pathlib import Path

class CubagemHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(Path(__file__).parent), **kwargs)
    
    def do_GET(self):
        if self.path == '/':
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            
            # Read the HTML template
            with open('templates/index.html', 'r', encoding='utf-8') as f:
                html_content = f.read()
            
            self.wfile.write(html_content.encode('utf-8'))
            
        elif self.path.startswith('/buscar'):
            # Parse query parameters
            parsed_url = urllib.parse.urlparse(self.path)
            query_params = urllib.parse.parse_qs(parsed_url.query)
            termo = query_params.get('q', [''])[0].lower()
            
            # Mock data since we can't use pandas
            mock_products = [
                {"Codigo": "001", "Nome": "Produto A", "m3_total": 0.5, "Peso": 10.0, "Comprimento": 50, "Largura": 40, "Altura": 25},
                {"Codigo": "002", "Nome": "Produto B", "m3_total": 1.2, "Peso": 25.0, "Comprimento": 80, "Largura": 60, "Altura": 25},
                {"Codigo": "003", "Nome": "Produto C", "m3_total": 0.8, "Peso": 15.0, "Comprimento": 40, "Largura": 50, "Altura": 40},
            ]
            
            # Filter products based on search term
            filtered = [p for p in mock_products if termo in p["Codigo"].lower() or termo in p["Nome"].lower()]
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(filtered).encode('utf-8'))
        else:
            super().do_GET()
    
    def do_POST(self):
        if self.path == '/cubagem':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))
            
            itens = data.get('itens', [])
            
            # Mock calculation
            caixas = [
                {"nome": "Caixa 12TP", "capacidade": 2.0},
                {"nome": "Caixa 15TP", "capacidade": 5.0},
                {"nome": "Caixa 19TP", "capacidade": 10.0},
            ]
            
            # Mock selected items
            mock_items = [
                {"Codigo": "001", "Nome": "Produto A", "m3_total": 0.5, "Peso": 10.0, "Comprimento": 50, "Largura": 40, "Altura": 25},
                {"Codigo": "002", "Nome": "Produto B", "m3_total": 1.2, "Peso": 25.0, "Comprimento": 80, "Largura": 60, "Altura": 25},
            ]
            
            volume_total = sum(item["m3_total"] for item in mock_items)
            peso_total = sum(item["Peso"] for item in mock_items)
            
            caixas_possiveis = [c for c in caixas if c["capacidade"] >= volume_total]
            
            result = {
                "itens_encontrados": len(mock_items),
                "volume_total": volume_total,
                "peso_total": peso_total,
                "caixas": caixas_possiveis,
                "itens": mock_items
            }
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(result).encode('utf-8'))

PORT = 8000

with socketserver.TCPServer(("", PORT), CubagemHandler) as httpd:
    print(f"Servidor rodando em http://localhost:{PORT}")
    httpd.serve_forever()