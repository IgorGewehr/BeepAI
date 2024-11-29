from fastapi import FastAPI

from router import router
import uvicorn

from utils import *

app = FastAPI()
app.include_router(router)

if __name__ == "__main__":
    manage_main_files()
    if not os.path.exists(IA_INI_FILE):
        initialize_ia_file()
    uvicorn.run(app, host="0.0.0.0", port=8000)



