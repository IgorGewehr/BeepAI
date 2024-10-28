from openai import OpenAI

def initializeOpenAI():
    client = OpenAI(
        api_key='sk-proj-k3Dtgxz3KLLkic_9TOlPdwmLLuvrhCyjT8w0sLcIMVim9olr_'
                'KUaAberm_hY0E4BgJqChSJMjmT3BlbkFJF1d-9gCUyzpPBarNr7yA-B_exHmD5i1BADD_'
                'WcME3RVtdwc139px0MoU4nxarrcLmYS7oCz90A')
    return client