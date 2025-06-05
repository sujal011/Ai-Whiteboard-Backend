"""
This file contains example Mermaid diagrams and their corresponding prompts for each diagram type.
These examples are used to help the AI model generate better diagrams by providing reference patterns.
"""

DIAGRAM_EXAMPLES = {
    "xychart-beta": {
        "prompt": "Create an XY chart showing monthly sales revenue with both bar and line charts",
        "example": """xychart-beta
    title "Sales Revenue"
    x-axis [jan, feb, mar, apr, may, jun, jul, aug, sep, oct, nov, dec]
    y-axis "Revenue (in $)" 4000 --> 11000
    bar [5000, 6000, 7500, 8200, 9500, 10500, 11000, 10200, 9200, 8500, 7000, 6000]
    line [5000, 6000, 7500, 8200, 9500, 10500, 11000, 10200, 9200, 8500, 7000, 6000]"""
    },
    
    "gantt": {
        "prompt": "Create a Gantt chart for a project timeline with multiple sections and dependencies",
        "example": """gantt
    title A Gantt Diagram
    dateFormat  YYYY-MM-DD
    section Section
    A task           :a1, 2014-01-01, 30d
    Another task     :after a1  , 20d
    section Another
    Task in sec      :2014-01-12  , 12d
    another task      : 24d"""
    },
    
    "sequenceDiagram": {
        "prompt": "Create a sequence diagram showing a conversation between two users with synchronous messages",
        "example": """sequenceDiagram
    Alice->>+John: Hello John, how are you?
    Alice->>+John: John, can you hear me?
    John-->>-Alice: Hi Alice, I can hear you!
    John-->>-Alice: I feel great!"""
    },
    
    "erDiagram": {
        "prompt": "Create an ER diagram for an e-commerce system showing relationships between customers, orders, and products",
        "example": """erDiagram
    CUSTOMER }|..|{ DELIVERY-ADDRESS : has
    CUSTOMER ||--o{ ORDER : places
    CUSTOMER ||--o{ INVOICE : "liable for"
    DELIVERY-ADDRESS ||--o{ ORDER : receives
    INVOICE ||--|{ ORDER : covers
    ORDER ||--|{ ORDER-ITEM : includes
    PRODUCT-CATEGORY ||--|{ PRODUCT : contains
    PRODUCT ||--o{ ORDER-ITEM : "ordered in" """
    },
    
    "mindmap": {
        "prompt": "Create a mind map about mind mapping tools and their history",
        "example": """mindmap
  root((mindmap))
    Origins
      Long history
      ::icon(fa fa-book)
      Popularisation
        British popular psychology author Tony Buzan
    Research
      On effectiveness<br/>and features
      On Automatic creation
        Uses
            Creative techniques
            Strategic planning
            Argument mapping
    Tools
      Pen and paper
      Mermaid"""
    },
    
    "flowchart": {
        "prompt": "Create a flowchart showing a decision tree for shopping choices",
        "example": """flowchart TD
    A[Christmas] -->|Get money| B(Go shopping)
    B --> C{Let me think}
    C -->|One| D[Laptop]
    C -->|Two| E[iPhone]
    C -->|Three| F[fa:fa-car Car]"""
    },
    
    "classDiagram": {
        "prompt": "Create a class diagram showing inheritance relationships between different animal types",
        "example": """classDiagram
    Animal <|-- Duck
    Animal <|-- Fish
    Animal <|-- Zebra
    Animal : +int age
    Animal : +String gender
    Animal: +isMammal()
    Animal: +mate()
    class Duck{
      +String beakColor
      +swim()
      +quack()
    }
    class Fish{
      -int sizeInFeet
      -canEat()
    }
    class Zebra{
      +bool is_wild
      +run()
    }"""
    },
    
    "gitGraph": {
        "prompt": "Create a git graph showing a feature branch workflow with merge",
        "example": """gitGraph
    commit
    commit
    branch develop
    checkout develop
    commit
    commit
    checkout main
    merge develop
    commit
    commit"""
    },
    
    "journey": {
        "prompt": "Create a journey diagram showing a daily work routine with different sections",
        "example": """journey
    title My working day
    section Go to work
      Make tea: 5: Me
      Go upstairs: 3: Me
      Do work: 1: Me, Cat
    section Go home
      Go downstairs: 5: Me
      Sit down: 3: Me"""
    },
    
    "pie": {
        "prompt": "Create a pie chart showing market share distribution",
        "example": """pie
    title Market Share Distribution
    "Product A" : 45
    "Product B" : 30
    "Product C" : 15
    "Others" : 10"""
    },
    
    "stateDiagram": {
        "prompt": "Create a state diagram for a vending machine",
        "example": """stateDiagram-v2
    [*] --> Idle
    Idle --> Processing: Insert Coin
    Processing --> Idle: Invalid Amount
    Processing --> Dispensing: Valid Amount
    Dispensing --> Idle: Item Dispensed
    Dispensing --> OutOfStock: No Items
    OutOfStock --> [*]"""
    }
}

def get_all_examples() -> dict:
    """Get all diagram examples and prompts."""
    return DIAGRAM_EXAMPLES 