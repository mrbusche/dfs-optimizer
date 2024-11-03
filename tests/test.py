import os

import pytest

from main import generate_lineup_files


@pytest.fixture(autouse=True)
def generate_files():
    generate_lineup_files()


def test_generate_lineup_files():
    assert os.path.exists('four_wr.csv')
    assert os.path.exists('three_rb.csv')
    assert os.path.exists('two_te.csv')


def test_four_wr():
    with open('four_wr.csv', 'r') as f:
        four_wr = [f.readline().strip() for _ in range(10)]

    conditions = [
        len(four_wr) == 10,
        four_wr[
            0] == "1,DST,Cardinals,2600,7.1,QB,Dak Prescott,6300,19.5,RB,Alvin and the Chipmunks,7800,22.9,RB,Matt Busche,7800,22.9,TE,Mike Gesicki,3100,10.6,WR,Cedric Tillman,4300,11.5,WR,Chris Olave,6100,17.0,WR,Drake London,6700,20.0,WR,Jakobi Meyers,5300,14.0,50000,145.5",
        four_wr[
            1] == "2,DST,Titans,3200,8.7,QB,Dak Prescott,6300,19.5,RB,Alvin and the Chipmunks,7800,22.9,RB,Kyren Williams,7000,21.1,TE,Mike Gesicki,3100,10.6,WR,Cedric Tillman,4300,11.5,WR,Chris Olave,6100,17.0,WR,Drake London,6700,20.0,WR,Jakobi Meyers,5300,14.0,49800,145.3",
        four_wr[
            2] == "3,DST,Titans,3200,8.7,QB,Jameis Winston,5400,17.4,RB,Chase from Paw Patrol,5900,17.9,RB,Kyren Williams,7000,21.1,TE,Mike Gesicki,3100,10.6,WR,Chris Olave,6100,17.0,WR,Drake London,6700,20.0,WR,Jakobi Meyers,5300,14.0,WR,Tyreek Hill,7300,18.6,50000,145.3",
        four_wr[
            3] == "4,DST,Cardinals,2600,7.1,QB,Lamar Jackson,8000,24.3,RB,Alvin and the Chipmunks,7800,22.9,RB,Chase from Paw Patrol,5900,17.9,TE,Mike Gesicki,3100,10.6,WR,Cedric Tillman,4300,11.5,WR,Chris Olave,6100,17.0,WR,Drake London,6700,20.0,WR,Jakobi Meyers,5300,14.0,49800,145.3",
        four_wr[
            4] == "5,DST,Cardinals,2600,7.1,QB,Lamar Jackson,8000,24.3,RB,Chase from Paw Patrol,5900,17.9,RB,Matt Busche,7800,22.9,TE,Mike Gesicki,3100,10.6,WR,Cedric Tillman,4300,11.5,WR,Chris Olave,6100,17.0,WR,Drake London,6700,20.0,WR,Jakobi Meyers,5300,14.0,49800,145.3",
        four_wr[
            5] == "6,DST,Titans,3200,8.7,QB,Dak Prescott,6300,19.5,RB,Kyren Williams,7000,21.1,RB,Matt Busche,7800,22.9,TE,Mike Gesicki,3100,10.6,WR,Cedric Tillman,4300,11.5,WR,Chris Olave,6100,17.0,WR,Drake London,6700,20.0,WR,Jakobi Meyers,5300,14.0,49800,145.3",
        four_wr[
            6] == "7,DST,Giants,2300,6.1,QB,Jameis Winston,5400,17.4,RB,Alvin and the Chipmunks,7800,22.9,RB,Kyren Williams,7000,21.1,TE,Mike Gesicki,3100,10.6,WR,Cedric Tillman,4300,11.5,WR,Chris Olave,6100,17.0,WR,Drake London,6700,20.0,WR,Tyreek Hill,7300,18.6,50000,145.2",
        four_wr[
            7] == "8,DST,Titans,3200,8.7,QB,Lamar Jackson,8000,24.3,RB,Alvin and the Chipmunks,7800,22.9,RB,Austin Powers,5300,16.2,TE,Mike Gesicki,3100,10.6,WR,Cedric Tillman,4300,11.5,WR,Chris Olave,6100,17.0,WR,Drake London,6700,20.0,WR,Jakobi Meyers,5300,14.0,49800,145.2",
        four_wr[
            8] == "9,DST,Titans,3200,8.7,QB,Lamar Jackson,8000,24.3,RB,Austin Powers,5300,16.2,RB,Matt Busche,7800,22.9,TE,Mike Gesicki,3100,10.6,WR,Cedric Tillman,4300,11.5,WR,Chris Olave,6100,17.0,WR,Drake London,6700,20.0,WR,Jakobi Meyers,5300,14.0,49800,145.2",
        four_wr[
            9] == "10,DST,Giants,2300,6.1,QB,Jameis Winston,5400,17.4,RB,Kyren Williams,7000,21.1,RB,Matt Busche,7800,22.9,TE,Mike Gesicki,3100,10.6,WR,Cedric Tillman,4300,11.5,WR,Chris Olave,6100,17.0,WR,Drake London,6700,20.0,WR,Tyreek Hill,7300,18.6,50000,145.2",
    ]

    assert all(conditions)


def test_three_rb():
    with open('three_rb.csv', 'r') as f:
        three_rb = [f.readline().strip() for _ in range(10)]

    conditions = [
        len(three_rb) == 10,
        three_rb[
            0] == "1,DST,Cardinals,2600,7.1,QB,Lamar Jackson,8000,24.3,RB,Austin Powers,5300,16.2,RB,Chase from Paw Patrol,5900,17.9,RB,Kyren Williams,7000,21.1,TE,Mike Gesicki,3100,10.6,WR,Chris Olave,6100,17.0,WR,Drake London,6700,20.0,WR,Jakobi Meyers,5300,14.0,50000,148.2",
        three_rb[
            1] == "2,DST,Cardinals,2600,7.1,QB,Jameis Winston,5400,17.4,RB,Alvin and the Chipmunks,7800,22.9,RB,Chase from Paw Patrol,5900,17.9,RB,Kyren Williams,7000,21.1,TE,Mike Gesicki,3100,10.6,WR,Chris Olave,6100,17.0,WR,Drake London,6700,20.0,WR,Jakobi Meyers,5300,14.0,49900,148.0",
        three_rb[
            2] == "3,DST,Cardinals,2600,7.1,QB,Jameis Winston,5400,17.4,RB,Chase from Paw Patrol,5900,17.9,RB,Kyren Williams,7000,21.1,RB,Matt Busche,7800,22.9,TE,Mike Gesicki,3100,10.6,WR,Chris Olave,6100,17.0,WR,Drake London,6700,20.0,WR,Jakobi Meyers,5300,14.0,49900,148.0",
        three_rb[
            3] == "4,DST,Titans,3200,8.7,QB,Jameis Winston,5400,17.4,RB,Alvin and the Chipmunks,7800,22.9,RB,Austin Powers,5300,16.2,RB,Kyren Williams,7000,21.1,TE,Mike Gesicki,3100,10.6,WR,Chris Olave,6100,17.0,WR,Drake London,6700,20.0,WR,Jakobi Meyers,5300,14.0,49900,147.9",
        three_rb[
            4] == "5,DST,Titans,3200,8.7,QB,Jameis Winston,5400,17.4,RB,Austin Powers,5300,16.2,RB,Kyren Williams,7000,21.1,RB,Matt Busche,7800,22.9,TE,Mike Gesicki,3100,10.6,WR,Chris Olave,6100,17.0,WR,Drake London,6700,20.0,WR,Jakobi Meyers,5300,14.0,49900,147.9",
        three_rb[
            5] == "6,DST,Cardinals,2600,7.1,QB,Justin Herbert,5300,17.2,RB,Alvin and the Chipmunks,7800,22.9,RB,Austin Powers,5300,16.2,RB,Matt Busche,7800,22.9,TE,Mike Gesicki,3100,10.6,WR,Chris Olave,6100,17.0,WR,Drake London,6700,20.0,WR,Jakobi Meyers,5300,14.0,50000,147.9",
        three_rb[
            6] == "7,DST,Cardinals,2600,7.1,QB,Gardner Minshew II,4500,14.7,RB,Alvin and the Chipmunks,7800,22.9,RB,Kyren Williams,7000,21.1,RB,Matt Busche,7800,22.9,TE,Mike Gesicki,3100,10.6,WR,Cedric Tillman,4300,11.5,WR,Chris Olave,6100,17.0,WR,Drake London,6700,20.0,49900,147.8",
        three_rb[
            7] == "8,DST,Cardinals,2600,7.1,QB,Justin Herbert,5300,17.2,RB,Alvin and the Chipmunks,7800,22.9,RB,Chase from Paw Patrol,5900,17.9,RB,Kyren Williams,7000,21.1,TE,Mike Gesicki,3100,10.6,WR,Chris Olave,6100,17.0,WR,Drake London,6700,20.0,WR,Jakobi Meyers,5300,14.0,49800,147.8",
        three_rb[
            8] == "9,DST,Cardinals,2600,7.1,QB,Justin Herbert,5300,17.2,RB,Chase from Paw Patrol,5900,17.9,RB,Kyren Williams,7000,21.1,RB,Matt Busche,7800,22.9,TE,Mike Gesicki,3100,10.6,WR,Chris Olave,6100,17.0,WR,Drake London,6700,20.0,WR,Jakobi Meyers,5300,14.0,49800,147.8",
        three_rb[
            9] == "10,DST,Cardinals,2600,7.1,QB,Dak Prescott,6300,19.5,RB,Alvin and the Chipmunks,7800,22.9,RB,Austin Powers,5300,16.2,RB,Matt Busche,7800,22.9,TE,Mike Gesicki,3100,10.6,WR,Cedric Tillman,4300,11.5,WR,Chris Olave,6100,17.0,WR,Drake London,6700,20.0,50000,147.7",
    ]

    assert all(conditions)


def test_two_te():
    with open('two_te.csv', 'r') as f:
        two_te = [f.readline().strip() for _ in range(10)]

    conditions = [
        len(two_te) == 10,
        two_te[
            0] == "1,DST,Titans,3200,8.7,QB,Lamar Jackson,8000,24.3,RB,Alvin and the Chipmunks,7800,22.9,RB,Kyren Williams,7000,21.1,TE,Mike Gesicki,3100,10.6,TE,Taysom Hill,3800,9.9,WR,Cedric Tillman,4300,11.5,WR,Chris Olave,6100,17.0,WR,Drake London,6700,20.0,50000,146.0",
        two_te[
            1] == "2,DST,Titans,3200,8.7,QB,Lamar Jackson,8000,24.3,RB,Kyren Williams,7000,21.1,RB,Matt Busche,7800,22.9,TE,Mike Gesicki,3100,10.6,TE,Taysom Hill,3800,9.9,WR,Cedric Tillman,4300,11.5,WR,Chris Olave,6100,17.0,WR,Drake London,6700,20.0,50000,146.0",
        two_te[
            2] == "3,DST,Cardinals,2600,7.1,QB,Lamar Jackson,8000,24.3,RB,Alvin and the Chipmunks,7800,22.9,RB,Matt Busche,7800,22.9,TE,AJ Barner,2600,7.2,TE,Mike Gesicki,3100,10.6,WR,Chris Olave,6100,17.0,WR,Drake London,6700,20.0,WR,Jakobi Meyers,5300,14.0,50000,146.0",
        two_te[
            3] == "4,DST,Titans,3200,8.7,QB,Justin Herbert,5300,17.2,RB,Alvin and the Chipmunks,7800,22.9,RB,Kyren Williams,7000,21.1,TE,David Njoku,5500,14.4,TE,Mike Gesicki,3100,10.6,WR,Chris Olave,6100,17.0,WR,Drake London,6700,20.0,WR,Jakobi Meyers,5300,14.0,50000,145.9",
        two_te[
            4] == "5,DST,Titans,3200,8.7,QB,Justin Herbert,5300,17.2,RB,Kyren Williams,7000,21.1,RB,Matt Busche,7800,22.9,TE,David Njoku,5500,14.4,TE,Mike Gesicki,3100,10.6,WR,Chris Olave,6100,17.0,WR,Drake London,6700,20.0,WR,Jakobi Meyers,5300,14.0,50000,145.9",
        two_te[
            5] == "6,DST,Titans,3200,8.7,QB,Lamar Jackson,8000,24.3,RB,Kyren Williams,7000,21.1,RB,Matt Busche,7800,22.9,TE,AJ Barner,2600,7.2,TE,Mike Gesicki,3100,10.6,WR,Chris Olave,6100,17.0,WR,Drake London,6700,20.0,WR,Jakobi Meyers,5300,14.0,49800,145.8",
        two_te[
            6] == "7,DST,Titans,3200,8.7,QB,Lamar Jackson,8000,24.3,RB,Alvin and the Chipmunks,7800,22.9,RB,Kyren Williams,7000,21.1,TE,AJ Barner,2600,7.2,TE,Mike Gesicki,3100,10.6,WR,Chris Olave,6100,17.0,WR,Drake London,6700,20.0,WR,Jakobi Meyers,5300,14.0,49800,145.8",
        two_te[
            7] == "8,DST,Titans,3200,8.7,QB,Dak Prescott,6300,19.5,RB,Alvin and the Chipmunks,7800,22.9,RB,Kyren Williams,7000,21.1,TE,David Njoku,5500,14.4,TE,Mike Gesicki,3100,10.6,WR,Cedric Tillman,4300,11.5,WR,Chris Olave,6100,17.0,WR,Drake London,6700,20.0,50000,145.7",
        two_te[
            8] == "9,DST,Titans,3200,8.7,QB,Dak Prescott,6300,19.5,RB,Kyren Williams,7000,21.1,RB,Matt Busche,7800,22.9,TE,David Njoku,5500,14.4,TE,Mike Gesicki,3100,10.6,WR,Cedric Tillman,4300,11.5,WR,Chris Olave,6100,17.0,WR,Drake London,6700,20.0,50000,145.7",
        two_te[
            9] == "10,DST,Cardinals,2600,7.1,QB,Lamar Jackson,8000,24.3,RB,Chase from Paw Patrol,5900,17.9,RB,Matt Busche,7800,22.9,TE,David Njoku,5500,14.4,TE,Mike Gesicki,3100,10.6,WR,Cedric Tillman,4300,11.5,WR,Chris Olave,6100,17.0,WR,Drake London,6700,20.0,50000,145.7",
    ]

    assert all(conditions)
