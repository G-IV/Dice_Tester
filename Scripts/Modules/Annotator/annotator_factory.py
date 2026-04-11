from Scripts.Modules.Annotator import annotator #, pips_by_pattern, pips_by_count

class AnnotateFactory:
    _registry = {
        "annotator": annotate.Annotator,
        #"pips_by_count": pips_by_count.Annotator
    }

    @classmethod
    def create_annotator(cls, annotator_type: str, **kwargs) -> annotate.Annotator:
        annotator_class = cls._registry.get(annotator_type)
        if not annotator_class:
            raise ValueError(f"Annotator type '{annotator_type}' is not registered.")
        return annotator_class(**kwargs)