#This file is licensed under the MIT No Attribution (MIT-0) License

# Define a data class to represent the prompt
class Prompt:
    def __init__(self, text, variables, examples):
         
         self.examples = examples
         self.text = text
         self.variables = variables

# Define a data class to represent the prompt
class PromptLibrary:
    def __init__(self):
     
            #Zero Shot Prompt
            prompt_text = """
                 You are a friendly and helpful chatbot. Respond to the user's message thoughtfully and concisely.  Use as few words as possible.`

                 User: {input}
                 Bot: 
                 """
            simplechat = Prompt(text=prompt_text, variables=["input"], examples='')

            #Zero Shot Prompt
            prompt_text = """
                 You are a friendly and helpful chatbot. Respond to the user's message thoughtfully and concisely.  Use as few words as possible.`

                 Current conversation:
                 {chat_history_lines}
                 User: {input}
                 Bot: 
                 """
            simplememorychat = Prompt(text=prompt_text, variables=["input","chat_history_lines"], examples='')

            #Few Shot Prompt with Examples

            examples = [{
                 "input": "I would like to place an order for some new equipment.",
                 "output": "new order",
           },{
                 "input": "I would like to buy.",
                 "output": "new order",
           },{
                 "input": "I need a refill.",
                 "output": "new order",
           },{
                 "input": "I would like to place and order.",
                 "output": "new order",
           },{
                 "input": "I would like to buy some more.",
                 "output": "new order",
           },{
                 "input": "I would like to order some.",
                 "output": "new order",
           },{
                 "input": "I need help placing an order.",
                 "output": "new order",
           },{
                 "input": "I would like some help placing an order.",
                 "output": "new order",
            },{
                 "input": "I would like to add some additional items to my order.",
                 "output": "order modification",
            },{
                 "input": "I would like to remove some items from my order.",
                 "output": "order modification",
            },{
                 "input": "I would like to change the delivery date.",
                 "output": "order modification",
            },{
                 "input": "I would like to change my delivery address.",
                 "output": "order modification",
            },{
                 "input": "I need to update the shipping address.",
                 "output": "order modification",
            },{
                 "input": "I need to delay my order delivery.",
                 "output": "order modification",
            },{
                 "input": "It has taken far too long for the items to ship, and as a result, I no longer want them.",
                 "output": "order cancellation",
            },{
                 "input": "I not longer want the items.",
                 "output": "order cancellation",
            },{
                 "input": "I not longer want the items.",
                 "output": "order cancellation",
            },{
                 "input": "I was charged too much for my order.",
                 "output": "order issue",
            },{
                 "input": "When my order arrived, items were damaged.",
                 "output": "order issue",
            },{
                 "input": "Why has my order delivery been delayed?",
                 "output": "order issue",
            },{
                 "input": "Why have my items not yet arrived?",
                 "output": "order issue",
            },{
                 "input": "Why has my order not yet arrived?",
                 "output": "order issue",
            },{
                 "input": "Why has my shipment not been sent?",
                 "output": "order issue",
            },{
                 "input": "What is the delay?",
                 "output": "order issue",
            },{
                 "input": "I would like some help with my order",
                 "output": "order issue",
            
            }]
            prompt_text = """
                 You are part of a sales order team.  Analyze the message to determine what kind of sales request is being made. Classify the request as either new order, order modification, order cancellation, or order issue. Be as concise as possible. You can only use one the phrases new order, order modification, order cancellation, or order issue when responding. Don't explain yourself, ask questions, or do anything but classify the user message.`

                 User: {input}
                 Bot: 
                 """
            webclassifier = Prompt(text=prompt_text, variables=["input"], examples=examples)

            prompt_text = """
                 As an expert copy-writer, you will write increasingly concise, entity-dense summaries of the user provided {input}. The initial summary should be under 50000 words and contain at least five informative Descriptive Entities from the {input} in english language.

                 A Descriptive Entity is:
                 - Relevant: to the main story.
                 - Specific: descriptive yet concise (5 words or fewer).
                 - Faithful: present in the {input}.
                 - Anywhere: located anywhere in the {input}.

                 # Your Summarization Process
                 - Use english as a language
                 - Read through the {input} and all the below sections to get an understanding of the task.
                 - Pick informative Descriptive Entities from the {input} (";" delimited, do not add spaces).
                 - In your output write an initial summary of max 50000 words containing the Entities.

                 Then, repeat the below steps multiple times.

                 - Step 1. In a new dict in the same list, identify one new informative Descriptive Entities from the {input} which are missing from the previously generated summary.
                 - Step 2. Write a new, denser summary of identical length which covers every Entity and detail from the previous summary plus the new Missing Entities.

                 A Missing Entity is:
                 - An informative Descriptive Entity from the {input} as defined above.
                 - Novel: not in the previous summary.

                 # Guidelines
                 - Make every word count: re-write the previous summary to improve flow and make space for additional entities.
                 - Make space with fusion, compression, and removal of uninformative phrases like "the {input} discusses".
                 - The summaries should become highly dense and concise yet self-contained, e.g., easily understood without the {input}.
                 - Missing entities can appear anywhere in the new summary.
                 - Never drop entities from the previous summary. If space cannot be made, add fewer new entities.
                 - Write the summary in english

                 # IMPORTANT
                 - Remember, to keep each summary to max 50000 words.
                 - Never remove Entities or details. Only add more from the {input}.
                 - Do not discuss the {input} itself, focus on the content: informative Descriptive Entities, and details.
                 - Remember, if you're overusing filler phrases in later summaries, or discussing the {input} itself, not its contents, choose more informative Descriptive Entities and include more details from the {input}.
                 """

            chain_of_density_content_generation = Prompt(text=prompt_text, variables=["input","chat_history_lines"], examples='')

            self.prompt = {
                "simplechat": simplechat,
                "simplememorychat": simplememorychat,
                "webclassifier": webclassifier,
                "webarticlewriter": chain_of_density_content_generation
            }