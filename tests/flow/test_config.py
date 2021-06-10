import os
import sys
import redis
from RLTest import Env
from redisgraph import Graph
from base import FlowTestsBase

redis_con = None
redis_graph = None

class testConfig(FlowTestsBase):
    def __init__(self):
        self.env = Env(decodeResponses=True)
        global redis_con
        global redis_graph
        redis_con = self.env.getConnection()
        redis_graph = Graph("config", redis_con)

    def test01_config_get(self):
        global redis_graph

        # Try reading 'MAINTAIN_TRANSPOSED_MATRICES' from config
        config_name = "MAINTAIN_TRANSPOSED_MATRICES"
        response = redis_con.execute_command("GRAPH.CONFIG GET " + config_name)
        expected_response = [config_name, 1]
        self.env.assertEqual(response, expected_response)

        # Try reading 'QUERY_MEM_CAPACITY' from config
        config_name = "QUERY_MEM_CAPACITY"
        response = redis_con.execute_command("GRAPH.CONFIG GET " + config_name)
        expected_response = [config_name, 0] # capacity=QUERY_MEM_CAPACITY_UNLIMITED
        self.env.assertEqual(response, expected_response)

        # Try reading all configurations
        config_name = "*"
        response = redis_con.execute_command("GRAPH.CONFIG GET " + config_name)
        # At least 10 configurations should be reported
        self.env.assertGreaterEqual(len(response), 10)

    def test02_config_get_invalid_name(self):
        global redis_graph

        # Ensure that getter fails on invalid parameters appropriately
        fake_config_name = "FAKE_CONFIG_NAME"

        try:
            redis_con.execute_command("GRAPH.CONFIG GET " + fake_config_name)
            assert(False)
        except redis.exceptions.ResponseError as e:
            # Expecting an error.
            assert("Unknown configuration field" in str(e))
            pass

    def test03_config_set(self):
        global redis_graph

        config_name = "RESULTSET_SIZE"
        config_value = 3

        # Set configuration
        response = redis_con.execute_command("GRAPH.CONFIG SET %s %d" % (config_name, config_value))
        self.env.assertEqual(response, "OK")

        # Make sure config been updated.
        response = redis_con.execute_command("GRAPH.CONFIG GET " + config_name)
        expected_response = [config_name, config_value]
        self.env.assertEqual(response, expected_response)


        config_name2 = "QUERY_MEM_CAPACITY"
        config_value2 = 1<<20 # 1NB

        # Set configuration
        response = redis_con.execute_command("GRAPH.CONFIG SET %s %d" % (config_name2, config_value2))
        self.env.assertEqual(response, "OK")

        # Make sure config been updated.
        response = redis_con.execute_command("GRAPH.CONFIG GET " + config_name2)
        expected_response = [config_name2, config_value2]
        self.env.assertEqual(response, expected_response)

        # Set multiple configurations
        config_value = 5
        config_value2 = 1<<30 # 1GB
        response = redis_con.execute_command("GRAPH.CONFIG SET %s %d %s %d" % (config_name, config_value, config_name2, config_value2))
        self.env.assertEqual(response, "OK")

        # Make sure 1st config been updated.
        response = redis_con.execute_command("GRAPH.CONFIG GET " + config_name)
        expected_response = [config_name, config_value]
        self.env.assertEqual(response, expected_response)

        # Make sure 2nd config been updated.
        response = redis_con.execute_command("GRAPH.CONFIG GET " + config_name2)
        expected_response = [config_name2, config_value2]
        self.env.assertEqual(response, expected_response)

    def test04_config_set_invalid_name(self):
        global redis_graph

        # Ensure that getter fails on invalid parameters appropriately
        fake_config_name = "FAKE_CONFIG_NAME"

        try:
            redis_con.execute_command("GRAPH.CONFIG SET " + fake_config_name + " 5")
            assert(False)
        except redis.exceptions.ResponseError as e:
            # Expecting an error.
            assert("Unknown configuration field" in str(e))
            pass

    def test05_config_invalid_subcommand(self):
        global redis_graph

        # Ensure failure on invalid sub-command, e.g. GRAPH.CONFIG DREP...
        config_name = "RESULTSET_SIZE"
        try:
            response = redis_con.execute_command("GRAPH.CONFIG DREP " + config_name + " 3")
            assert(False)
        except redis.exceptions.ResponseError as e:
            assert("Unknown subcommand for GRAPH.CONFIG" in str(e))
            pass

