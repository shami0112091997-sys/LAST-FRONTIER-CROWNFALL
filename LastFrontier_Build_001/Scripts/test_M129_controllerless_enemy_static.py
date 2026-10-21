#!/usr/bin/env python3
"""Static regression for controllerless six-enemy pursuit (NOT an Unreal compile/run).

Read files within this repository only; do not mutate the project.
"""
from pathlib import Path

project = Path(__file__).resolve().parents[1]
enemy = (project / 'Source/LastFrontier/Private/Enemy/LFEnemy.cpp').read_text()
world = (project / 'Source/LastFrontier/Private/World/LFWorldDirector.cpp').read_text()
project_descriptor = (project / 'LastFrontier.uproject').read_text()

checks = [
    ('enemy uses AddMovementInput', 'AddMovementInput(Delta.GetSafeNormal(), 1.0f)' in enemy),
    ('controllerless movement is enabled exactly once',
     enemy.count('bRunPhysicsWithNoController = true;') == 1),
    ('movement flag set before BeginPlay',
     enemy.index('bRunPhysicsWithNoController = true;') < enemy.index('void ALFEnemy::BeginPlay()')),
    ('enemy constructor still orients to chase direction',
     'bOrientRotationToMovement = true;' in enemy),
    ('enemy spawn is controllerless in current level director',
     'SpawnActor<ALFEnemy>(' in world),
    ('no experimental GooglePAD change bundled into gameplay branch',
     '"Plugins":' not in project_descriptor),
]
for title, passed in checks:
    if not passed:
        raise AssertionError('M129_STATIC_CHECK_FAILED: ' + title)
print('M129_STATIC_REGRESSION=PASS (6 checks; Unreal compile and Android execution NOT performed)')
