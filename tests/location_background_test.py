

from unittest import TestCase

from worldnavigator.locations.base_location import LocationBackground


class LocationBackgroundTest(TestCase):
  def test_background_creation(self):
    """
    Test that LocationBackground correctly initializes with various background configurations.

    Arrange:
      - Create background configurations with different combinations of day/afternoon/night

    Act:
      - Initialize LocationBackground instances with these configurations

    Assert:
      - Verify backgrounds are set correctly
      - Verify default values are applied when backgrounds are not specified
    """
    # Test with only day background
    bg_day_only = LocationBackground({'day': 'bg_day'})
    self.assertEqual(bg_day_only.day, 'bg_day')
    self.assertEqual(bg_day_only.afternoon, 'bg_day')  # Should default to day
    self.assertEqual(bg_day_only.night, 'bg_day')      # Should default to day

    # Test with all backgrounds specified
    bg_all = LocationBackground({
        'day': 'bg_day',
        'afternoon': 'bg_afternoon',
        'night': 'bg_night'
    })
    self.assertEqual(bg_all.day, 'bg_day')
    self.assertEqual(bg_all.afternoon, 'bg_afternoon')
    self.assertEqual(bg_all.night, 'bg_night')

    # Test get_backgrounds method
    self.assertEqual(bg_all.get_backgrounds(), ('bg_day', 'bg_afternoon', 'bg_night'))

  def test_retrieve_scene_background(self):
    """
    Test that the correct background is retrieved based on the time of day.

    Arrange:
      - Create a LocationBackground with different backgrounds for different times

    Act:
      - Call retrieve_scene_background with different times

    Assert:
      - Verify the correct background is returned for each time period
    """
    bg = LocationBackground({
        'day': 'bg_day',
        'afternoon': 'bg_afternoon',
        'night': 'bg_night'
    })

    # Test morning/day (7:00 - 16:59)
    self.assertEqual(bg.retrieve_scene_background((7, 0)), 'bg_day')
    self.assertEqual(bg.retrieve_scene_background((12, 30)), 'bg_day')
    self.assertEqual(bg.retrieve_scene_background((16, 59)), 'bg_day')

    # Test afternoon (17:00 - 18:59)
    self.assertEqual(bg.retrieve_scene_background((17, 0)), 'bg_afternoon')
    self.assertEqual(bg.retrieve_scene_background((18, 30)), 'bg_afternoon')
    self.assertEqual(bg.retrieve_scene_background((18, 59)), 'bg_afternoon')

    # Test night (19:00 - 6:59)
    self.assertEqual(bg.retrieve_scene_background((19, 0)), 'bg_night')
    self.assertEqual(bg.retrieve_scene_background((23, 45)), 'bg_night')
    self.assertEqual(bg.retrieve_scene_background((0, 0)), 'bg_night')
    self.assertEqual(bg.retrieve_scene_background((6, 59)), 'bg_night')
