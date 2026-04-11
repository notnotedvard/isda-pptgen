from manim import *

# Configuration for 1080p by default (1920x1080, 16:9).
# To render in 4K, you can run Manim with the `-qk` flag (e.g. `manim -qk scripts/manim_thermometers.py ThermometerSlide`)
config.pixel_height = 1080
config.pixel_width = 1920
config.frame_height = 8.0
config.frame_width = 8.0 * 16 / 9
# config.background_color = "#111111"  # Dark mode background
config.media_dir = "media"  # Output saved to media folder

class ThermometerSlide(Scene):
    def construct(self):
        # Add background image
        bg = ImageMobject("assets/slide_bg.png")
        bg.scale_to_fit_width(config.frame_width)
        self.add(bg)

        # Input Data: (Title, Goal, To-Date)
        # ...existing code...
        data = [
            ("Local Church Budget", 150000, 124500),
            ("Building Fund", 50000, 12000),
            ("Conference Advance", 25000, 25000),
        ]

        # Main Title
        title = Text("Tithes and Offerings", font_size=64, weight=BOLD, color=WHITE)
        title.to_edge(UP, buff=0.4)
        self.add(title)

        thermometers_group = VGroup()

        # Parameters for thermometer visualization
        therm_width = 1.0
        therm_height = 4.0
        anim_duration = 2.0
        stagger_delay = 0.3

        animations = []
        for i, (name, goal, to_date) in enumerate(data):
            percentage = min(to_date / goal, 1.0)
            
            # Value tracker for the animation counting up from 0 to 'to_date'
            tracker = ValueTracker(0)

            # Container Group for a single thermometer
            single_group = VGroup()

            # Name Text above
            name_text = Text(name, font_size=24, color=WHITE)
            
            # Goal Text above the thermometer
            goal_text = Text(f"Goal: ${goal:,}", font_size=24, color=LIGHT_GREY)

            # Outline of the thermometer
            outline = RoundedRectangle(
                width=therm_width, 
                height=therm_height, 
                corner_radius=therm_width/2, 
                color=WHITE, 
                stroke_width=4
            )

            # Fill shape
            # Using a simple Rectangle for fill to avoid RoundedRectangle artifacts during scaling
            fill = Rectangle(
                width=therm_width - 0.2, 
                height=0.01, 
                color=BLUE_C, 
                fill_opacity=1, 
                stroke_width=0
            )
            # Position the initial fill at the bottom of the outline
            fill.move_to(outline.get_bottom() + UP * 0.1, aligned_edge=DOWN)

            # Updater function to scale the fill based on the tracker's value
            def update_fill(f, tr=tracker, outline=outline, goal=goal):
                current_val = tr.get_value()
                current_pct = min(current_val / goal, 1.0)
                # Avoid height 0 to prevent rendering glitches
                new_height = max(current_pct * (therm_height - 0.2), 0.01)
                
                f.stretch_to_fit_height(new_height, about_edge=DOWN)
                # Re-anchor to the bottom
                f.move_to(outline.get_bottom() + UP * 0.1, aligned_edge=DOWN)

            fill.add_updater(update_fill)

            # To-Date Counter Text below the thermometer
            counter = DecimalNumber(
                0,
                show_ellipsis=False,
                num_decimal_places=0,
                include_sign=False,
                group_with_commas=True,
                font_size=32,
                color=GREEN_C
            )
            # Add updater to the counter decimal value
            counter.add_updater(lambda d, tr=tracker: d.set_value(tr.get_value()))
            
            # Subtitle text below the counter
            to_date_label = Text("To Date", font_size=20, color=LIGHT_GREY)

            # Assemble the individual group vertically
            name_text.next_to(outline, UP, buff=0.9)
            goal_text.next_to(outline, UP, buff=0.3)
            counter.next_to(outline, DOWN, buff=0.3)
            to_date_label.next_to(counter, DOWN, buff=0.2)
            
            # Explicitly center the texts and counter to the outline's X position
            name_text.match_x(outline)
            goal_text.match_x(outline)
            counter.match_x(outline)
            to_date_label.match_x(outline)
            
            single_group.add(name_text, goal_text, outline, fill, counter, to_date_label)
            thermometers_group.add(single_group)

            # Prepare the animation queue for this thermometer
            animations.append(
                tracker.animate(run_time=anim_duration, rate_func=smooth).set_value(to_date)
            )

        # Arrange the 3 thermometers equally horizontally and center them in the frame
        thermometers_group.arrange(RIGHT, buff=2.0)
        thermometers_group.move_to(ORIGIN).shift(DOWN * 0.3)
        
        # Initial draw (fading in static elements)
        self.play(FadeIn(title), FadeIn(thermometers_group), run_time=0.5)
        
        # Play the staggered animations
        self.play(
            AnimationGroup(*animations, lag_ratio=stagger_delay / anim_duration),
            run_time=anim_duration + stagger_delay * (len(animations) - 1)
        )

        # Let the final state chill on screen for a moment
        self.wait(1)