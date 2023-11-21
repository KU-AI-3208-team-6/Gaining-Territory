import math
import time
from itertools import combinations, product, chain
from shapely.geometry import LineString, Point, Polygon


class MACHINE:
    """
    [ MACHINE ]
    MinMax Algorithm을 통해 수를 선택하는 객체.
    - 모든 Machine Turn마다 변수들이 업데이트 됨

    ** To Do **
    MinMax Algorithm을 이용하여 최적의 수를 찾는 알고리즘 생성
       - class 내에 함수를 추가할 수 있음
       - 최종 결과는 find_best_selection을 통해 Line 형태로 도출
           * Line: [(x1, y1), (x2, y2)] -> MACHINE class에서는 x값이 작은 점이 항상 왼쪽에 위치할 필요는 없음 (System이 organize 함)
    """

    def __init__(self, whole_points=[], location=[]):
        self.id = "MACHINE"
        self.score = [0, 0]  # USER, MACHINE
        self.drawn_lines = []  # Drawn Lines
        self.board_size = 7  # 7 x 7 Matrix
        self.num_dots = 0
        self.whole_points = whole_points
        self.location = location
        self.triangles = []  # [(a, b), (c, d), (e, f)]

        # Precomputing all possible lines to draw in the object creation step
        self.drawable_lines = [
            [dot1, dot2]
            for (dot1, dot2) in list(combinations(self.whole_points, 2))
            if self.check_availability([dot1, dot2])
        ]

    """
    `drawn_lines`, `whole_points`, `triangles`은 System으로부터 주입받음
    System이 `find_best_selection`이 선택한 Line을 Draw
    """

    def find_best_selection(self):
        if self.drawable_lines:
            # The last element is always the last line added,
            # because the system works by appending new_line to drawn_line
            newly_drawn_line = self.drawn_lines[-1]
            # Update the list of lines that can be drawn based on the newly drawn line
            self.update_drawable_lines(newly_drawn_line)

        choice = []
        if len(self.drawable_lines) > 13:
            choice = self.min_max(limit=3)
        else:
            choice = self.min_max(limit=-1)

        self.update_drawable_lines(choice)
        return choice

    def min_max(self, limit):
        def step_machine(cutoff, cur_limit):
            best_value = -math.inf
            best_choice = None

            choosable_lines = self.drawable_lines
            for choice in choosable_lines:
                cur_value = 0
                if self.does_earn_point(choice):
                    cur_value += 1

                deleted_lines = self.update_drawable_lines(choice)

                if self.drawable_lines and cur_limit != 0:
                    cur_value += step_user(best_value, cur_limit - 1)[0]

                self.drawable_lines += deleted_lines

                if cur_value > best_value:
                    best_value = cur_value
                    best_choice = choice

                    if best_value >= cutoff:
                        break

            return (best_value, best_choice)

        def step_user(cutoff, cur_limit):
            worst_value = math.inf
            worst_choice = None

            choosable_lines = self.drawable_lines
            for choice in choosable_lines:
                cur_value = 0
                if self.does_earn_point(choice):
                    cur_value -= 1

                deleted_lines = self.update_drawable_lines(choice)

                if self.drawable_lines and cur_limit != 0:
                    cur_value += step_machine(worst_value, cur_limit - 1)[0]

                self.drawable_lines += deleted_lines

                if cur_value < worst_value:
                    worst_value = cur_value
                    worst_choice = choice

                    if worst_value <= cutoff:
                        break

            return (worst_value, worst_choice)

        start_time = time.perf_counter()
        expectation, choice = step_machine(math.inf, limit)
        end_time = time.perf_counter()
        print(
            "selection : {choice}, expection : {expectation}, depth : {depth} - ({time}ms)".format(
                choice=choice,
                expectation=expectation,
                depth=limit,
                time=int(round((end_time - start_time) * 1000)),
            )
        )
        return choice

    def check_availability(self, line):
        line_string = LineString(line)
        dot1, dot2 = line

        # Must be one of the whole points
        if (dot1 not in self.whole_points) or (dot2 not in self.whole_points):
            return False

        # Must not skip a dot
        for dot in self.whole_points:
            if dot == dot1 or dot == dot2:
                continue
            else:
                if bool(line_string.intersection(Point(dot))):
                    return False

        # Must not cross another line
        for drawn_line in self.drawn_lines:
            if len(set([dot1, dot2, *drawn_line])) == 3:
                continue
            elif bool(line_string.intersection(LineString(drawn_line))):
                return False

        # Must be a new line
        if line in self.drawn_lines:
            return False

        return True

    def does_earn_point(self, line):
        dot1, dot2 = line

        lines_consist_dot1 = []
        lines_consist_dot2 = []

        # Check the line to be drawn and the line to be connected
        for drawn_line in self.drawn_lines:
            # Since we're checking for new lines to draw,
            # they shouldn't be in the list of already drawn lines.
            # Might need to be added if the logic changes in the future
            # if drawn_line == line:
            #     continue

            if dot1 in drawn_line:
                lines_consist_dot1.append(drawn_line)
            if dot2 in drawn_line:
                lines_consist_dot2.append(drawn_line)

        # Triangles cannot be formed if there is no other line connecting them on either side
        if not lines_consist_dot1 or not lines_consist_dot2:
            return False

        # Search for triangles created that don't have a point inside them
        for line1, line2 in product(lines_consist_dot1, lines_consist_dot2):
            vertices = set([dot1, dot2, *line1, *line2])

            if len(vertices) != 3:
                continue

            isEmpty = True
            for dot in self.whole_points:
                if dot in vertices:
                    continue
                if bool(Polygon(chain(line, line1, line2)).intersection(Point(dot))):
                    isEmpty = False
                    break

            # Find triangles that meet the criteria
            if isEmpty:
                return True

        # Failed to find a triangle that met the conditions
        return False

    def update_drawable_lines(self, newly_drawn_line):
        line_string = LineString(newly_drawn_line)

        old_drawable_lines = self.drawable_lines
        self.drawable_lines = []

        deleted_lines = []
        for line in old_drawable_lines:
            if len(set([*newly_drawn_line, *line])) == 3:
                self.drawable_lines.append(line)
            elif not bool(line_string.intersection(LineString(line))):
                self.drawable_lines.append(line)
            else:
                deleted_lines.append(line)
        return deleted_lines
