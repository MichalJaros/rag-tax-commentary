# server.py
from typing import List
import litserve as ls
from vllm import LLM, SamplingParams
from transformers import AutoTokenizer

class SimpleLitAPI(ls.LitAPI):
    def setup(self, device):
        model_id = "speakleash/Bielik-11B-v2.3-Instruct-FP8"
        self.tokenizer = AutoTokenizer.from_pretrained(model_id)
        self.llm = LLM(model=model_id, max_model_len=4096)

    def predict(self, prompt: List[dict]):
        sampling_params = SamplingParams(temperature=0.2, top_p=0.95, max_tokens=4096)
        prompts = self.tokenizer.apply_chat_template(prompt, tokenize=False)
        outputs = self.llm.generate(prompts, sampling_params)
        generated_text = outputs[0].outputs[0].text
        yield generated_text

# (STEP 2) - START THE SERVER::wq

if __name__ == "__main__":
    # scale with advanced features (batching, GPUs, etc...)
    server = ls.LitServer(SimpleLitAPI(), accelerator="auto", max_batch_size=1, spec=ls.OpenAISpec())
    server.run(port=8000)