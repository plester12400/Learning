import psycopg2
from collections import defaultdict


class OptionValidator:
    def __init__(self, options_dict):
        self.options_dict = options_dict

    def validate(self, list_of_options):
        output = []
        for o in list_of_options:
            excluded = self.options_dict.get(o, [])
            matches = [x for x in excluded]
            if matches:
                for match in matches:
                    if match in list_of_options:
                        output.append('Option {} is not compatible with {}'.format(o, match))
        return output


class OptionsDao:
    @staticmethod
    def get_options_with_exclusions():
        query = """select id, name, description, exclude_video_option_id, 
       (select name from video_options where voe.exclude_video_option_id = id) as excluded_name
            from video_options vo
            left outer join video_options_excludes voe on vo.id = voe.video_option_id;
"""
        conn = psycopg2.connect(dbname='postgres', host='localhost', port=5432, user='postgres', password='password')
        cursor = conn.cursor()
        cursor.execute(query)
        results = cursor.fetchall()
        if results:
            dd = defaultdict(set)
            for r in results:
                the_id, the_name, _, excluded, excluded_name = r
                if excluded:
                    dd[the_name].add(excluded_name)
            return dd


if __name__ == "__main__":
    print(OptionsDao.get_options_with_exclusions())
    ov = OptionValidator(OptionsDao.get_options_with_exclusions())
    blah = ['AUDIO_FADE_IN', 'VIDEO_FADE_IN', 'AUDIO_FADE_IN_OUT', 'CROSS_FADE']
    print(ov.validate(blah))
