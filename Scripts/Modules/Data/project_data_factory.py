from Scripts.Modules.Data import project_data, pips_by_count, pips_by_pattern

class ProjectDataFactory:
    _registry = {
        "project_data": project_data.ProjectData,
        "pips_by_count": pips_by_count.ProjectData,
        "pips_by_pattern": pips_by_pattern.ProjectData
    }

    @classmethod
    def create_project_data(cls, data_type: str, **kwargs) -> project_data.ProjectData:
        data_class = cls._registry.get(data_type)
        if not data_class:
            raise ValueError(f"Data type '{data_type}' is not registered.")
        return data_class(**kwargs)