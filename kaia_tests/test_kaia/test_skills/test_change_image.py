import json
from unittest import TestCase
from kaia.eaglesong.core import Automaton, Scenario, Image
from kaia.kaia.skills.change_image_skill import ChangeImageIntents, ChangeImageSkill
from kaia.kaia.skills import KaiaTestAssistant
from kaia.avatar import AvatarTestApi, AvatarSettings, NewContentStrategy, MediaLibraryManager
from kaia.brainbox import MediaLibrary
from kaia.infra import Loc

def check_image(tag):
    def _check(arg, tc: TestCase):
        tc.assertIsInstance(arg, Image)
        d = json.loads(arg.data)
        tc.assertEqual(tag, d['tag'])
    return _check


class ChangeImageTestCase(TestCase):
    def test_change_image(self):
        with Loc.create_temp_file('tests/change_image/library', 'zip', True) as media_library:
            tags = {str(i): {'character': 'character_0', 'tag': i} for i in range(3)}
            MediaLibrary.generate(media_library, tags)
            with Loc.create_temp_file('tests/change_image/stats','json') as stats_file:
                manager = MediaLibraryManager(NewContentStrategy(False), media_library, stats_file)
                with AvatarTestApi(AvatarSettings(image_media_library_manager=manager)) as api:
                    (
                        Scenario(lambda: Automaton(KaiaTestAssistant([ChangeImageSkill(api)]), None))
                        .send(ChangeImageIntents.change_image.utter())
                        .check(check_image(0))
                        .send(ChangeImageIntents.change_image.utter())
                        .check(check_image(1))
                        .send(ChangeImageIntents.bad_image.utter())
                        .check(check_image(2))
                        .send(ChangeImageIntents.change_image.utter())
                        .check(check_image(0))
                        .send(ChangeImageIntents.change_image.utter())
                        .check(check_image(2))
                        .validate()
                    )