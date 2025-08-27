import os
import openai
from dotenv import load_dotenv

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

def load_prompt_template():
    with open("prompt_template.txt", "r") as f:
        return f.read()

def generate_cypher_query(user_question):
    prompt = load_prompt_template()

    # ✅ FULL GRAPH SCHEMA (ESCAPED CURLY BRACES FOR .format() SAFETY)
    graph_schema = """
        Nodes:
          (:Part {{name}})
          (:BikeModel {{name}})
          (:BikeType {{name}})

        Relationships:
          (:Part)-[:USED_IN {{{{quantity, price}}}}]->(:BikeModel)
          (:BikeModel)-[:IS_A]->(:BikeType)

        Example Data:
        MERGE (p:Part {{{{name: 'Engine Assembly'}}}})
        MERGE (m:BikeModel {{{{name: 'Classic 350'}}}})
        MERGE (t:BikeType {{{{name: 'Cruiser'}}}})
        MERGE (p)-[:USED_IN {{{{quantity: 1, price: 32412.0}}}}]->(m)
        MERGE (m)-[:IS_A]->(t)

        MERGE (p:Part {{{{name: 'Clutch Plate'}}}})
        MERGE (m:BikeModel {{{{name: 'Classic 350'}}}})
        MERGE (t:BikeType {{{{name: 'Cruiser'}}}})
        MERGE (p)-[:USED_IN {{{{quantity: 3, price: 833.0}}}}]->(m)
        MERGE (m)-[:IS_A]->(t)

        MERGE (p:Part {{{{name: 'Brake Pads'}}}})
        MERGE (m:BikeModel {{{{name: 'Bullet 350'}}}})
        MERGE (t:BikeType {{{{name: 'Standard'}}}})
        MERGE (p)-[:USED_IN {{{{quantity: 3, price: 1290.0}}}}]->(m)
        MERGE (m)-[:IS_A]->(t)

        MERGE (p:Part {{{{name: 'Chain Sprocket Kit'}}}})
        MERGE (m:BikeModel {{{{name: 'Hunter 350'}}}})
        MERGE (t:BikeType {{{{name: 'Roadster'}}}})
        MERGE (p)-[:USED_IN {{{{quantity: 3, price: 2614.0}}}}]->(m)
        MERGE (m)-[:IS_A]->(t)

        MERGE (p:Part {{{{name: 'Front Suspension'}}}})
        MERGE (m:BikeModel {{{{name: 'Meteor 350'}}}})
        MERGE (t:BikeType {{{{name: 'Cruiser'}}}})
        MERGE (p)-[:USED_IN {{{{quantity: 2, price: 4020.0}}}}]->(m)
        MERGE (m)-[:IS_A]->(t)

        MERGE (p:Part {{{{name: 'Rear Suspension'}}}})
        MERGE (m:BikeModel {{{{name: 'Meteor 350'}}}})
        MERGE (t:BikeType {{{{name: 'Cruiser'}}}})
        MERGE (p)-[:USED_IN {{{{quantity: 2, price: 3780.0}}}}]->(m)
        MERGE (m)-[:IS_A]->(t)

        MERGE (p:Part {{{{name: 'Silencer'}}}})
        MERGE (m:BikeModel {{{{name: 'Classic 350'}}}})
        MERGE (t:BikeType {{{{name: 'Cruiser'}}}})
        MERGE (p)-[:USED_IN {{{{quantity: 1, price: 4560.0}}}}]->(m)
        MERGE (m)-[:IS_A]->(t)

        MERGE (p:Part {{{{name: 'Handlebar'}}}})
        MERGE (m:BikeModel {{{{name: 'Hunter 350'}}}})
        MERGE (t:BikeType {{{{name: 'Roadster'}}}})
        MERGE (p)-[:USED_IN {{{{quantity: 1, price: 870.0}}}}]->(m)
        MERGE (m)-[:IS_A]->(t)

        MERGE (p:Part {{{{name: 'Headlight'}}}})
        MERGE (m:BikeModel {{{{name: 'Bullet 350'}}}})
        MERGE (t:BikeType {{{{name: 'Standard'}}}})
        MERGE (p)-[:USED_IN {{{{quantity: 1, price: 1450.0}}}}]->(m)
        MERGE (m)-[:IS_A]->(t)

        MERGE (p:Part {{{{name: 'Fuel Tank'}}}})
        MERGE (m:BikeModel {{{{name: 'Meteor 350'}}}})
        MERGE (t:BikeType {{{{name: 'Cruiser'}}}})
        MERGE (p)-[:USED_IN {{{{quantity: 1, price: 5290.0}}}}]->(m)
        MERGE (m)-[:IS_A]->(t)
        """.strip()

    formatted_prompt = prompt.replace("<GRAPH_SCHEMA>", graph_schema).format(question=user_question)

    response = openai.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": formatted_prompt}],
        temperature=0.2
    )
    return response.choices[0].message.content.strip()
