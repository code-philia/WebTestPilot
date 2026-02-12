from typing import Any, get_origin

from pydantic import BaseModel, model_validator


class Symbol(BaseModel):
    """
    Specialized BaseModel that:
    1. Allows None for any field without raising ValidationError.
    2. Fills in field defaults if provided.
    3. Ignores extra fields (from LLM hallucinations).
    """
    model_config = {
        "extra": "ignore", 
        "populate_by_name": True,
    }

    @model_validator(mode="before")
    @classmethod
    def none_to_default(cls, data: Any) -> dict:
        """
        Convert None to field default if available, otherwise skip field.
        Handles all types (bool, int, str, list, dict, etc.).
        """
        if not isinstance(data, dict):
            return data
        
        new_data = {}
        for name, field in cls.model_fields.items():
            val = data.get(name, None)
            if val is None:
                # Use default if available
                if field.default is not None:
                    new_data[name] = field.default

                # Coerce based on field type
                else:
                    origin = get_origin(field.annotation)
                    ann = field.annotation
                    if origin is list or ann == list:
                        new_data[name] = []
                    elif origin is dict or ann == dict:
                        new_data[name] = {}
                    elif origin is set or ann == set:
                        new_data[name] = set()
                    else:
                        # fallback: skip (treated as missing)
                        pass
  
            else:
                new_data[name] = val

        return new_data