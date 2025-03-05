import argparse

from openai import OpenAI

client = OpenAI(
    # This is the default and can be omitted
    api_key="####"
)


if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--input", type=str)
    parser.add_argument("-o", "--output", type=str)
    args = parser.parse_args()

    pipe_out = open("../llm-guidance/g2v", "w")
    pipe_in = open("../llm-guidance/v2g", "r")

    history = []
    temperature = 0.0

    # model = "gpt-4"
    model = "gpt-4-0125-preview"

    while True:
        cmd = pipe_in.readline()[:-1]
        if cmd == "":
            break

        # connect testing
        if cmd == "hello":
            pipe_out.write("hello_end\n")
            pipe_out.flush()

        # create a new robot (forget the history)
        elif cmd == "new":
            history = []
            pipe_out.write("new_end\n")
            pipe_out.flush()

        # set temperature
        elif cmd == "temperature":
            t = float(pipe_in.readline()[:-1])
            temperature = t
            pipe_out.write("temperature_end\n")
            pipe_out.flush()

        # ask to gpt
        # before asking, the prompt should be prepared in 'input' history
        elif cmd == "prompt":
            # read input
            with open(args.input, "r") as file:
                prompt = file.read()

            history.append({"role": "user", "content": prompt})

            # print(history)

            response = client.chat.completions.create(
                model=model, messages=history, temperature=temperature
            )
            answer = response.choices[0].message.content

            # write answer back
            with open(args.output, "w") as f:
                f.write(answer)

            history.append({"role": "assistant", "content": answer})

            # print(answer)

            pipe_out.write("prompt_end\n")
            pipe_out.flush()

        # final operation
        elif cmd == "exit":
            break
