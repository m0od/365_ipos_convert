import uvicorn

host = "0.0.0.0"
port = 6000
app_name = "app.main:app"
reload = True

if __name__ == '__main__':
    uvicorn.run(app_name, host=host, port=port, reload=reload,
                ssl_keyfile="privkey.pem",
                ssl_certfile="cert.pem"
                )
