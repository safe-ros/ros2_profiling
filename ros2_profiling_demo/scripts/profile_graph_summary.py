#!/usr/bin/env python3

import argparse
import sys

from ros2profile.api.process import load_mcap_data, load_event_graph


def summarize(graph):
    for node in graph.nodes():
        print(f'Node: {node.name()}')
        if node.publishers():
            print(f'  Publishers: ')
            for publisher in node.publishers():
                print(f'    Topic: {publisher.topic_name()}')
                print(f'      Events: {len(publisher.events())}')
        if node.subscriptions():
            print(f'  Subscriptions: ')
            for subscription in node.subscriptions():
                print(f'    Topic: {subscription.topic_name()}')
                print(f'      Callback: {subscription.callback().symbol()}')
        if node.timers():
            print(f'  Timers: ')
            for timer in node.timers():
                print(f'    Period: {timer.period()}')
                print(f'      Callback: {timer.callback().symbol()}')
                print(f'      Events: {len(timer.callback().events())}')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("profile", type=str, help="Profile directory")
    args = parser.parse_args()
    graph = load_event_graph(args.profile)
    summarize(graph)

if __name__ == '__main__':
    main()
