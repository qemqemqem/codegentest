class Config:

    def __init__(self, config_file):
        config = {}
        with open(config_file) as f:
            # Iterate through lines
            for line in f:
                # Break on colons
                line = line.split(':')
                # Remove whitespace
                line = [x.strip() for x in line]
                # Add to config
                config[line[0].lower()] = line[1]
        self.name = config['name'] if 'name' in config else 'Untitled'
        self.description = config['description'] if 'description' in config else "I'm learning to program videogames in pygame. Please give me a simple programming task."
        self.technology = config['technology'] if 'technology' in config else ''
        self.auto_debug = config['auto_debug'].lower() == "true" if 'auto_debug' in config else True
        self.auto_test = config['auto_test'].lower() == "true" if 'auto_test' in config else True
        self.model = config['model'] if 'model' in config else 'gpt-3.5-turbo'
