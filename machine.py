import random
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

    def __init__(
        self, score=[0, 0], drawn_lines=[], whole_lines=[], whole_points=[], location=[]
    ):
        self.id = "MACHINE"
        self.score = [0, 0]  # USER, MACHINE
        self.drawn_lines = []  # Drawn Lines
        self.board_size = 7  # 7 x 7 Matrix
        self.num_dots = 0
        self.whole_points = []
        self.location = []
        self.triangles = []  # [(a, b), (c, d), (e, f)]

    """
    `drawn_lines`, `whole_points`, `triangles`은 System으로부터 주입받음
    System이 `find_best_selection`이 선택한 Line을 Draw
    """

    def find_best_selection(self):
        """
        아래의 원래 코드는 Brute Force
        """
        available = [
            [point1, point2]
            for (point1, point2) in list(combinations(self.whole_points, 2))
            if self.check_availability([point1, point2])
        ]
        return random.choice(available)

    def check_availability(self, line):
        line_string = LineString(line)
        dot1, dot2 = line

        # Must be one of the whole points
        if (dot1 not in self.whole_points) or (dot2 not in self.whole_points):
            return False

        # Must not skip a dot
        for point in self.whole_points:
            if point == dot1 or point == dot2:
                continue
            else:
                if bool(line_string.intersection(Point(point))):
                    return False

        # Must not cross another line
        for drawn_line in self.drawn_lines:
            if len(set([dot1, dot2, drawn_line[0], drawn_line[1]])) == 3:
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
            vertices = set([dot1, dot2, line1[0], line1[1], line2[0], line2[1]])

            if len(vertices) != 3:
                continue

            isEmpty = True
            for dot in self.whole_points:
                if dot in vertices:
                    continue
                if bool(Polygon(chain(*[line, line1, line2])).intersection(Point(dot))):
                    isEmpty = False
                    break

            # Find triangles that meet the criteria
            if isEmpty:
                return True

        # Failed to find a triangle that met the conditions
        return False
