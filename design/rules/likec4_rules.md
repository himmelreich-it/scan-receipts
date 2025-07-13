# LikeC4 DSL Rules and Instructions for Code Agents

## Overview
LikeC4 is a Domain-Specific Language (DSL) for describing software architecture based on the C4 model. It compiles architecture descriptions into visual diagrams and supports both `.likec4` and `.c4` file extensions.

## Core File Structure

### 1. Top-Level Structure
```likec4
specification {
  // Define element types and relationship kinds
}

model {
  // Define architecture elements and relationships
}

views {
  // Define diagram views and styling
}
```

## Specification Rules

### Element Types
- Must define element types in the `specification` block
- Common element types: `person`, `system`, `container`, `component`, `element`
- Syntax: `element <elementType>`

### Relationship Kinds (Optional)
- Define relationship semantics for better modeling
- Syntax: `relationship <relationshipKind>`
- Examples: `async`, `uses`, `graphql`, `rest`

## Model Rules

### Element Definition
**Basic Syntax:**
```likec4
elementName = elementType 'Display Title' {
  description 'Element description'
  technology 'Technology used'
}
```

**Naming Rules:**
- Element names can contain letters, digits, and underscores
- Cannot start with a digit
- Cannot contain dots (`.`)
- Must be unique within their scope

**Properties:**
- `title`: Display name (optional, defaults to element name)
- `description`: Descriptive text
- `technology`: Technology specification
- `metadata`: Key-value pairs for additional data

### Nested Elements
Elements can contain other elements (containers):
```likec4
system mySystem {
  container webApp {
    component frontend
    component backend
  }
}
```

### Relationship Rules

**Basic Relationship Syntax:**
```likec4
source -> target 'relationship description'
```

**Extended Relationship Syntax:**
```likec4
source -> target 'relationship description' {
  title 'Display title'
  description 'Detailed description'
  technology 'HTTP/REST'
  tags #tag1 #tag2
}
```

**Relationship Kinds:**
```likec4
// Using defined relationship kinds
source -[async]-> target
source .uses target  // prefix notation
```

**Nested Relationships:**
- Can be defined within element blocks
- Use `this` or `it` to reference parent element
- Support "sourceless" relationships (parent as implicit source)

```likec4
customer = actor {
  -> frontend 'opens browser'  // customer -> frontend
  it -> backend 'API calls'    // customer -> backend
}
```

## Reference Rules

### Scope and Hoisting
- LikeC4 uses lexical scope with hoisting (like JavaScript)
- Elements are hoisted within their scope
- Elements "bubble up" to parent scopes if unique
- Top-level elements are globally available

### Fully Qualified Names (FQN)
- Use dot notation for disambiguation: `service1.api`
- Required when element names are ambiguous across scopes

### Reference Resolution
```likec4
model {
  service1 = service {
    api = component
  }
  service2 = service {
    api = component
  }
  
  // Ambiguous - will cause error
  // frontend -> api
  
  // Explicit - correct
  frontend -> service1.api
}
```

## Views and Styling Rules

### View Definition
```likec4
views {
  view viewName {
    title 'View Title'
    description 'View description'
    include *  // or specific elements
  }
}
```

### Styling Properties
- `color`: Element color (primary, muted, custom)
- `shape`: rectangle, person, cylinder, etc.
- `size`: xsmall, small, medium, large, xlarge
- `icon`: Icon specification
- `opacity`: Transparency level
- `border`: Border styling

## Error Prevention Rules

### Common Syntax Errors to Avoid
1. **Missing relationship operator**: Use `->` not `=` or other operators
2. **Invalid element names**: No spaces, special characters (except underscore)
3. **Ambiguous references**: Always use FQN when elements aren't unique
4. **Missing quotes**: String values must be quoted
5. **Incorrect nesting**: Ensure proper block structure with `{}`

### Validation Rules
1. **Element uniqueness**: Names must be unique within scope
2. **Reference validity**: All referenced elements must exist
3. **Relationship endpoints**: Both source and target must be valid elements
4. **Technology specification**: Should be meaningful and consistent

## Code Agent Instructions

### When Creating LikeC4 Files:
1. **Always start with specification block** defining element types
2. **Use meaningful element names** that reflect architecture
3. **Include descriptions** for clarity and documentation
4. **Define relationships explicitly** with clear descriptions
5. **Organize elements hierarchically** using nested containers
6. **Use consistent naming conventions** throughout the model

### When Debugging LikeC4 Files:
1. **Check element name uniqueness** within scopes
2. **Verify all references exist** and are properly scoped
3. **Ensure relationship syntax** uses `->` operator
4. **Validate element type definitions** in specification
5. **Check for missing quotes** around string values
6. **Verify proper block nesting** and syntax

### Best Practices:
1. **Use semantic relationship kinds** for better expressiveness
2. **Group related elements** in containers
3. **Apply consistent styling** across views
4. **Document element purposes** with descriptions
5. **Use tags for categorization** and filtering
6. **Keep element names concise** but descriptive

## Example Template
```likec4
specification {
  element person
  element system
  element container
  element component
  
  relationship async
  relationship uses
}

model {
  user = person 'End User' {
    description 'System user'
  }
  
  mySystem = system 'My System' {
    description 'Main application system'
    
    webApp = container 'Web Application' {
      technology 'React'
      
      frontend = component 'Frontend' {
        technology 'React/TypeScript'
      }
      
      backend = component 'Backend API' {
        technology 'Node.js'
      }
    }
  }
  
  // Relationships
  user -> mySystem.webApp.frontend 'Uses web interface'
  mySystem.webApp.frontend -[async]-> mySystem.webApp.backend 'API calls'
}

views {
  view systemView {
    title 'System Overview'
    include *
  }
}
```

## File Extensions
- Use `.likec4` or `.c4` extensions
- Multiple files are merged into single model
- Support for extending models across files