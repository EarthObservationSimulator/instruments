"""Unit tests for instrupy.util module.
"""

import json
import os
import sys
import unittest

import numpy
from instrupy.util import *

class TestEntity(unittest.TestCase):
  
    class ChildClass(Entity):            
        def __init__(self):
            self._id = 123
            self.name = "Ramesh"
            self.record = {"workexp": 5, "area": "electrical"}
            super(TestEntity.ChildClass,self).__init__(self._id, "TestClass")
    
    def test_eq(self):
        self.assertNotEqual(Entity(), Entity())
        self.assertNotEqual(Entity(), Entity(_id="test"))
        self.assertNotEqual(Entity(_id="test"), Entity())
        self.assertNotEqual(Entity(_id="foo"), Entity(_id="bar"))
        self.assertEqual(Entity(_id="test"), Entity(_id="test"))

    def test_hash(self):
        self.assertNotEqual(hash(Entity(_id="foo")), hash(Entity(_id="bar")))
        self.assertEqual(hash(Entity(_id="test")), hash(Entity(_id="test")))

    def test_to_dict(self):
        d = Entity().to_dict()
        self.assertEqual(d.get("@type"), "Entity")
        self.assertIsNone(d.get("@id"))

    def test_to_dict_id(self):
        d = Entity(_id="test").to_dict()
        self.assertEqual(d.get("@id"), "test")

        d = Entity(_id=123).to_dict()
        self.assertEqual(d.get("@id"),123)

        d = Entity(_id="123").to_dict()
        self.assertEqual(d.get("@id"),"123")
    
    def test_to_dict_childclass(self):                
        x = TestEntity.ChildClass()
        d = x.to_dict()
        self.assertEqual(d.get("@id"), 123)
        self.assertEqual(d.get("@type"), "TestClass")
        self.assertEqual(d.get("name"), "Ramesh")
        self.assertEqual(d.get("record").get("workexp"), 5)
        self.assertEqual(d.get("record").get("area"), "electrical")

    def test_from_dict(self):
        o = Entity.from_dict({})
        self.assertEqual(o._type, "Entity")
        self.assertIsNone(o._id)

    def test_from_dict_id(self):
        o = Entity.from_dict(dict({"@id": "test"}))
        self.assertEqual(o._id, "test")

        o = Entity.from_dict(dict({"@id": 123}))
        self.assertEqual(o._id, 123)

        o = Entity.from_dict(dict({"@id": "123"}))
        self.assertEqual(o._id, "123")    
        
    def test_to_json(self):
        d = json.loads(Entity().to_json())
        self.assertEqual(d.get("@type"), "Entity")
        self.assertIsNone(d.get("@id"))       

    def test_to_json_id(self):
        d = json.loads(Entity(_id="test").to_json())
        self.assertEqual(d.get("@id"), "test")

        d = json.loads(Entity(_id=123).to_json())
        self.assertEqual(d.get("@id"),123)

        d = json.loads(Entity(_id="123").to_json())
        self.assertEqual(d.get("@id"),"123")
    
    def test_to_json_childclass(self):                
        x = TestEntity.ChildClass()
        d = json.loads(x.to_json())
        self.assertEqual(d.get("@id"), 123)
        self.assertEqual(d.get("@type"), "TestClass")
        self.assertEqual(d.get("name"), "Ramesh")
        self.assertEqual(d.get("record").get("workexp"), 5)
        self.assertEqual(d.get("record").get("area"), "electrical")

    def test_from_json(self):
        o = Entity.from_json('{}')
        self.assertEqual(o._type, "Entity")
        self.assertIsNone(o._id)

    def test_from_json_id(self):
        o = Entity.from_json('{"@id": "test"}')
        self.assertEqual(o._id, "test")

        o = Entity.from_json('{"@id": 123}')
        self.assertEqual(o._id, 123)

        o = Entity.from_json('{"@id": "123"}')
        self.assertEqual(o._id, "123")

class TestOrientation(unittest.TestCase):

    def test_from_json_basic(self):        
        # Test valid nominal case
        o = Orientation.from_json(
                '{"referenceFrame": "SC_BODY_FIXED", "convention": "SIDE_LOOK","sideLookAngle":10, "@id": 123}')
        self.assertEqual(o._type, "Orientation")
        self.assertEqual(o._id, 123)
        self.assertEqual(o.ref_frame, ReferenceFrame.get("SC_BODY_FIXED"))
        self.assertEqual(o.euler_angle2, 10)
        # No reference frame specification
        o = Orientation.from_json(
                '{"convention": "SIDE_LOOK","sideLookAngle":10, "@id": 123}')
        self.assertEqual(o._type, "Orientation")
        self.assertEqual(o._id, 123)
        self.assertEqual(o.ref_frame, ReferenceFrame.get("NADIR_POINTING"))
        self.assertEqual(o.euler_angle2, 10)        
        # Test for wrong convention specification
        with self.assertRaises(Exception):
            Orientation.from_json(
                '{"referenceFrame": "NADIR_POINTING", "convention": "SIDE_LOOK1","sideLookAngle":10}')
        with self.assertRaises(Exception):
            Orientation.from_json(
                '{"referenceFrame": "NADIR_POINTING", "convention": "XXZ","xRotation":10,"yRotation":-10.4,"zRotation":20.78}')
        # Test for case-insensitivity
        o = Orientation.from_json(
            '{"referenceFrame": "NADIR_POINTING", "convention": "SIDE_look","sideLookAngle":10}')
        self.assertEqual(o._type, "Orientation")
        self.assertIsNone(o._id)
        self.assertEqual(o.euler_angle2, 10)
        # Test wraping of angle values to [0, 360]deg range.
        o = Orientation.from_json(
            '{"referenceFrame": "NADIR_POINTING", "convention": "XYz","xRotation":10,"yRotation":-10.4,"zRotation":20.78}')
        self.assertEqual(o._type, "Orientation")
        self.assertIsNone(o._id)
        self.assertEqual(o.euler_angle2, 360-10.4)

    def test_from_json_SIDELOOKANGLE_convention(self):
        # Test for positive angle less than 360 deg
        o = Orientation.from_json(
            '{"referenceFrame": "SC_BODY_FIXED", "convention": "SIDE_LOOK","sideLookAngle":10}')
        self.assertEqual(o.ref_frame, ReferenceFrame.get("SC_BODY_FIXED"))
        self.assertEqual(o.euler_angle1, 0)
        self.assertEqual(o.euler_angle2, 10)
        self.assertEqual(o.euler_angle3, 0)
        self.assertEqual(o.euler_seq1, 1)
        self.assertEqual(o.euler_seq2, 2)
        self.assertEqual(o.euler_seq3, 3)
        self.assertEqual(o._type, "Orientation")
        self.assertIsNone(o._id)
        # Test for negative angle
        o = Orientation.from_json(
            '{"referenceFrame": "SC_BODY_FIXED", "convention": "SIDE_LOOK","sideLookAngle":-10}')
        self.assertEqual(o.ref_frame, ReferenceFrame.get("SC_BODY_FIXED"))
        self.assertEqual(o.euler_angle1, 0)
        self.assertEqual(o.euler_angle2, 350)
        self.assertEqual(o.euler_angle3, 0)
        self.assertEqual(o.euler_seq1, 1)
        self.assertEqual(o.euler_seq2, 2)
        self.assertEqual(o.euler_seq3, 3)
        self.assertEqual(o._type, "Orientation")
        self.assertIsNone(o._id)
        # Test for positive angle greater than 360 deg
        o = Orientation.from_json(
            '{"referenceFrame": "NADIR_POINTING", "convention": "SIDE_LOOK","sideLookAngle":380}')
        self.assertEqual(o.ref_frame, ReferenceFrame.get("NADIR_POINTING"))
        self.assertEqual(o.euler_angle1, 0)
        self.assertEqual(o.euler_angle2, 20)
        self.assertEqual(o.euler_angle3, 0)
        self.assertEqual(o.euler_seq1, 1)
        self.assertEqual(o.euler_seq2, 2)
        self.assertEqual(o.euler_seq3, 3)
        self.assertEqual(o._type, "Orientation")
        self.assertIsNone(o._id)
        # Test for negative angle less than -360 deg
        o = Orientation.from_json(
            '{"convention": "SIDE_LOOK","sideLookAngle":-380}')
        self.assertEqual(o.ref_frame, ReferenceFrame.get("NADIR_POINTING"))
        self.assertEqual(o.euler_angle1, 0)
        self.assertEqual(o.euler_angle2, 340)
        self.assertEqual(o.euler_angle3, 0)
        self.assertEqual(o.euler_seq1, 1)
        self.assertEqual(o.euler_seq2, 2)
        self.assertEqual(o.euler_seq3, 3)
        self.assertEqual(o._type, "Orientation")
        self.assertIsNone(o._id)
        # Test for no convention specification
        with self.assertRaises(Exception):
            Orientation.from_json('{"sideLookAngle":-30}')

    def test_from_json_XYZ_convention(self):
        # Test for positive, negative angles
        o = Orientation.from_json(
            '{"referenceFrame": "EARTH_CENTERED_INERTIAL", "convention": "XYZ","xRotation":10,"yRotation":-10.4,"zRotation":20.78}')
        self.assertEqual(o.ref_frame, ReferenceFrame.get("EARTH_CENTERED_INERTIAL"))
        self.assertEqual(o.euler_angle1, 10)
        self.assertEqual(o.euler_angle2, 349.6)
        self.assertEqual(o.euler_angle3, 20.78)
        self.assertEqual(o.euler_seq1, 1)
        self.assertEqual(o.euler_seq2, 2)
        self.assertEqual(o.euler_seq3, 3)
        self.assertEqual(o._type, "Orientation")
        self.assertIsNone(o._id)
        # Test for positive angles greater than 360 deg, negative angles lesser than -360 deg
        o = Orientation.from_json(
            '{"referenceFrame": "EARTH_CENTERED_INERTIAL", "convention": "XYZ","xRotation":410,"yRotation":1045.8,"zRotation":-458}')
        self.assertEqual(o.ref_frame, ReferenceFrame.get("EARTH_CENTERED_INERTIAL"))
        self.assertEqual(o.euler_angle1, 50)
        self.assertAlmostEqual(o.euler_angle2, 325.8)
        self.assertEqual(o.euler_angle3, 262)
        self.assertEqual(o.euler_seq1, 1)
        self.assertEqual(o.euler_seq2, 2)
        self.assertEqual(o.euler_seq3, 3)
        self.assertEqual(o._type, "Orientation")
        self.assertIsNone(o._id)
    
    def test_from_json_REF_FRAME_ALIGNED_convention(self):
        o = Orientation.from_json(
            '{"referenceFrame": "NADIR_POINTING", "convention": "REF_FRAME_ALIGNED"}')
        self.assertEqual(o.ref_frame, ReferenceFrame.get("NADIR_POINTING"))
        self.assertEqual(o.euler_angle1, 0)
        self.assertEqual(o.euler_angle2, 0)
        self.assertEqual(o.euler_angle3, 0)
        self.assertEqual(o.euler_seq1, 1)
        self.assertEqual(o.euler_seq2, 2)
        self.assertEqual(o.euler_seq3, 3)
        self.assertEqual(o._type, "Orientation")
        self.assertIsNone(o._id)

        o = Orientation.from_json(
            '{"referenceFrame": "SC_BODY_FIXED", "convention": "REF_FRAME_ALIGNED"}')
        self.assertEqual(o.ref_frame, ReferenceFrame.get("SC_BODY_FIXED"))
        self.assertEqual(o.euler_angle1, 0)
        self.assertEqual(o.euler_angle2, 0)
        self.assertEqual(o.euler_angle3, 0)
        self.assertEqual(o._type, "Orientation")
        self.assertIsNone(o._id)

    def test_from_json_EULER_convention(self):
        o = Orientation.from_json(
            '{"referenceFrame": "SC_BODY_FIXED", "convention": "EULER","eulerAngle1":400,"eulerAngle2":1345.8, \
              "eulerAngle3":-458,"eulerSeq1":3, "eulerSeq2":1, "eulerSeq3":3}')
        self.assertEqual(o.ref_frame, ReferenceFrame.get("SC_BODY_FIXED"))
        self.assertEqual(o.euler_angle1, 40)
        self.assertAlmostEqual(o.euler_angle2, 265.8)
        self.assertEqual(o.euler_angle3, 262)
        self.assertEqual(o.euler_seq1, 3)
        self.assertEqual(o.euler_seq2, 1)
        self.assertEqual(o.euler_seq3, 3)
        self.assertEqual(o._type, "Orientation")
        self.assertIsNone(o._id)

    def test_to_dict(self):
        # SIDE_LOOK convention
        o = Orientation.from_json(
            '{"referenceFrame": "SC_BODY_FIXED", "convention": "SIDE_LOOK","sideLookAngle":10}')
        d = o.to_dict()
        self.assertEqual(d["referenceFrame"], "SC_BODY_FIXED")
        self.assertEqual(d["convention"], "EULER")
        self.assertEqual(d["eulerAngle1"], 0)
        self.assertAlmostEqual(d["eulerAngle2"], 10)
        self.assertEqual(d["eulerAngle3"], 0)
        self.assertEqual(d["eulerSeq1"], 1)
        self.assertEqual(d["eulerSeq2"], 2)
        self.assertEqual(d["eulerSeq3"], 3)
        self.assertIsNone(d["@id"])
        # XYZ convention
        o = Orientation.from_json(
            '{"referenceFrame": "EARTH_CENTERED_INERTIAL", "convention": "XYZ","xRotation":-10,"yRotation":-78.2,"zRotation":-20.5}')
        d = o.to_dict()
        self.assertEqual(d["referenceFrame"], "EARTH_CENTERED_INERTIAL")
        self.assertEqual(d["convention"], "EULER")
        self.assertEqual(d["eulerAngle1"], 350)
        self.assertAlmostEqual(d["eulerAngle2"], 281.8)
        self.assertEqual(d["eulerAngle3"], 339.5)
        self.assertEqual(d["eulerSeq1"], 1)
        self.assertEqual(d["eulerSeq2"], 2)
        self.assertEqual(d["eulerSeq3"], 3)
        self.assertIsNone(d["@id"])
        # REF_FRAME_ALIGNED convention
        o = Orientation.from_json(
            '{"referenceFrame": "NADIR_POINTING", "convention": "REF_FRAME_ALIGNED", "@id":"123"}')
        d = o.to_dict()
        self.assertEqual(d["referenceFrame"], "NADIR_POINTING")
        self.assertEqual(d["convention"], "EULER")
        self.assertEqual(d["eulerAngle1"], 0)
        self.assertAlmostEqual(d["eulerAngle2"], 0)
        self.assertEqual(d["eulerAngle3"], 0)
        self.assertEqual(d["eulerSeq1"], 1)
        self.assertEqual(d["eulerSeq2"], 2)
        self.assertEqual(d["eulerSeq3"], 3)
        self.assertEqual(d["@id"], "123")
        # EULER convention
        o = Orientation.from_json(
            '{"referenceFrame": "SC_BODY_FIXED", "convention": "EULER","eulerAngle1":400,"eulerAngle2":1345.8, \
              "eulerAngle3":-458,"eulerSeq1":3, "eulerSeq2":1, "eulerSeq3":3, "@id":123}')
        d = o.to_dict()
        self.assertEqual(d["referenceFrame"], "SC_BODY_FIXED")
        self.assertEqual(d["convention"], "EULER")
        self.assertEqual(d["eulerAngle1"], 40)
        self.assertAlmostEqual(d["eulerAngle2"], 265.8)
        self.assertEqual(d["eulerAngle3"], 262)
        self.assertEqual(d["eulerSeq1"], 3)
        self.assertEqual(d["eulerSeq2"], 1)
        self.assertEqual(d["eulerSeq3"], 3)
        self.assertEqual(d["@id"], 123)
                
    def test___repr__(self):
        # _id = None
        o = Orientation.from_json(
            '{"referenceFrame": "SC_BODY_FIXED", "convention": "EULER","eulerAngle1":400,"eulerAngle2":20, \
              "eulerAngle3":-458,"eulerSeq1":3, "eulerSeq2":1, "eulerSeq3":3}')
        self.assertEqual(o.__repr__(), "Orientation(ref_frame='SC_BODY_FIXED',euler_angle1=40.0,euler_angle2=20.0,euler_angle3=262.0,euler_seq1=3,euler_seq2=1,euler_seq3=3,_id=None)")
        # _id = 123 (integer)
        o = Orientation.from_json('{"referenceFrame": "NADIR_POINTING", "convention": "REF_FRAME_ALIGNED", "@id": 123}')
        self.assertEqual(o.__repr__(), "Orientation(ref_frame='NADIR_POINTING',euler_angle1=0.0,euler_angle2=0.0,euler_angle3=0.0,euler_seq1=1,euler_seq2=2,euler_seq3=3,_id=123)")
        # _id = 123 (string)
        o = Orientation.from_json('{"convention": "SIDE_LOOK","sideLookAngle":-380,"@id":"123"}')
        self.assertEqual(o.__repr__(), "Orientation(ref_frame='NADIR_POINTING',euler_angle1=0.0,euler_angle2=340.0,euler_angle3=0.0,euler_seq1=1,euler_seq2=2,euler_seq3=3,_id='123')")

class TestSphericalGeometry(unittest.TestCase):

    def test_from_json_custom_specs(self):
        # Test for typical case
        o = SphericalGeometry.from_json(
            '{"shape": "CUSTOM", "customConeAnglesVector": [10,10,10,10] , "customClockAnglesVector": [30,60,180,220]}')
        self.assertIsInstance(o, SphericalGeometry)
        self.assertIs(o.shape, SphericalGeometry.Shape.CUSTOM)
        self.assertEqual(o.cone_angle_vec, [10, 10, 10, 10])
        self.assertEqual(o.clock_angle_vec, [30, 60, 180, 220])
        self.assertIsNone(o.angle_height)
        self.assertIsNone(o.angle_width)
        self.assertIsNone(o._id)

        o = SphericalGeometry.from_json(
            '{"shape": "Custom", "customConeAnglesVector": [10], "@id": 123}')
        self.assertIsInstance(o, SphericalGeometry)
        self.assertIs(o.shape, SphericalGeometry.Shape.CUSTOM)
        self.assertEqual(o.cone_angle_vec, [10])
        self.assertIsNone(o.clock_angle_vec)
        self.assertIsNone(o.angle_height)
        self.assertIsNone(o.angle_width)
        self.assertEqual(o._id, 123)

        o = SphericalGeometry.from_json(
            '{"shape": "CusTOM", "customConeAnglesVector": 10, "@id": "123"}')
        self.assertIsInstance(o, SphericalGeometry)
        self.assertIs(o.shape, SphericalGeometry.Shape.CUSTOM)
        self.assertEqual(o.cone_angle_vec, [10])
        self.assertIsNone(o.clock_angle_vec)
        self.assertIsNone(o.angle_height)
        self.assertIsNone(o.angle_width)
        self.assertEqual(o._id, "123")

        # test Exception is raised for invalid cone, clock angle inputs
        with self.assertRaises(Exception):
            SphericalGeometry.from_json(
                '{"shape": "CUSTOM", "customConeAnglesVector": [10] , "customClockAnglesVector": [30]}')
        with self.assertRaises(Exception):
            SphericalGeometry.from_json(
                '{"shape": "CUSTOM", "customConeAnglesVector": 10 , "customClockAnglesVector": 30}')
        with self.assertRaises(Exception):
            SphericalGeometry.from_json(
                '{"shape": "CUSTOM", "customConeAnglesVector": [10,10,100] , "customClockAnglesVector": [30,60,180,220]}')

    def test_from_json_circular_specs(self):
        # Test for typical case
        o = SphericalGeometry.from_json(
            '{"shape": "CIRCULAR", "diameter": 30.56}')
        self.assertIsInstance(o, SphericalGeometry)
        self.assertIs(o.shape, SphericalGeometry.Shape.CIRCULAR)
        self.assertEqual(o.cone_angle_vec, [15.28])
        self.assertIsNone(o.clock_angle_vec)
        self.assertEqual(o.angle_height, 30.56)
        self.assertEqual(o.angle_width, 30.56)
        self.assertIsNone(o._id)        

        o = SphericalGeometry.from_json(
            '{"shape": "Circular", "diameter": 15.4242, "@id":123}')
        self.assertIsInstance(o, SphericalGeometry)
        self.assertIs(o.shape, SphericalGeometry.Shape.CIRCULAR)
        self.assertEqual(o.cone_angle_vec, [7.7121])
        self.assertIsNone(o.clock_angle_vec)
        self.assertIsNone(o.clock_angle_vec)
        self.assertEqual(o.angle_height, 15.4242)
        self.assertEqual(o.angle_width, 15.4242)
        self.assertEqual(o._id, 123)

        o = SphericalGeometry.from_json(
            '{"shape": "CirCuLar", "diameter": 25, "@id":"123"}')
        self.assertIsInstance(o, SphericalGeometry)
        self.assertIs(o.shape, SphericalGeometry.Shape.CIRCULAR)
        self.assertEqual(o.cone_angle_vec, [12.5])
        self.assertIsNone(o.clock_angle_vec)
        self.assertIsNone(o.clock_angle_vec)
        self.assertEqual(o.angle_height, 25)
        self.assertEqual(o.angle_width, 25)
        self.assertEqual(o._id, "123")
        # Test for incomplete specification
        with self.assertRaises(Exception):
            SphericalGeometry.from_json('{"shape": "CIRCULAR"}')
        # Test for full cone angle more than 180 deg
        with self.assertRaises(Exception):
            SphericalGeometry.from_json(
                '{"shape": "CIRCULAR", "diameter": 230}')
        # Test for full cone angle less than 0 deg
        with self.assertRaises(Exception):
            SphericalGeometry.from_json(
                '{"shape": "CIRCULAR", "diameter": -10}')        

    def test_from_json_rectangular_specs(self):
        # Test for typical cases
        o = SphericalGeometry.from_json(
            '{"shape": "RECTANGULAR", "angleHeight": 10 , "angleWidth": 30}')
        self.assertIsInstance(o, SphericalGeometry)
        self.assertIs(o.shape, SphericalGeometry.Shape.RECTANGULAR)
        self.assertAlmostEqual(o.cone_angle_vec, [
                         15.79322415135941, 15.79322415135941, 15.79322415135941, 15.79322415135941])
        self.assertAlmostEqual(o.clock_angle_vec, [
                         18.6768081421232, 161.3231918578768, 198.6768081421232, 341.3231918578768])
        self.assertEqual(o.angle_height, 10)
        self.assertAlmostEqual(o.angle_width, 30)
        self.assertIsNone(o._id)

        # Square FOV => Clock angle almost(?) 45 deg
        o = SphericalGeometry.from_json(
            '{"shape": "RECTANGULAR", "angleHeight": 15 , "angleWidth": 15, "@id": 123}')
        self.assertIsInstance(o, SphericalGeometry)
        self.assertIs(o.shape, SphericalGeometry.Shape.RECTANGULAR)
        self.assertAlmostEqual(o.cone_angle_vec, [
                         10.591411134810208, 10.591411134810208, 10.591411134810208, 10.591411134810208])
        self.assertAlmostEqual(o.clock_angle_vec, [
                         45.246138033024906, 134.75386196697508, 225.24613803302492, 314.7538619669751])
        self.assertAlmostEqual(o.angle_height, 15)
        self.assertAlmostEqual(o.angle_width, 15)
        self.assertEqual(o._id, 123)

        # angleWidth > angleHeight
        o = SphericalGeometry.from_json(
            '{"shape": "RECTANGULAR", "angleHeight": 30 , "angleWidth": 10}')
        self.assertIsInstance(o, SphericalGeometry)
        self.assertIs(o.shape, SphericalGeometry.Shape.RECTANGULAR)
        self.assertAlmostEqual(o.cone_angle_vec, [
                         15.79322415135941, 15.79322415135941, 15.79322415135941, 15.79322415135941])
        self.assertAlmostEqual(o.clock_angle_vec, [
                         71.98186515628623, 108.01813484371377, 251.98186515628623, 288.01813484371377])
        self.assertAlmostEqual(o.angle_height, 30)
        self.assertAlmostEqual(o.angle_width, 10)
        self.assertIsNone(o._id)

        # Test a edge case when the along-track fov is very small.
        o = SphericalGeometry.from_json(
            '{"shape": "RECTANGULAR", "angleHeight": 0.1 , "angleWidth": 50, "@id": "123"}')
        self.assertIsInstance(o, SphericalGeometry)
        self.assertIs(o.shape, SphericalGeometry.Shape.RECTANGULAR)
        self.assertAlmostEqual(o.cone_angle_vec[0], 25, 2)
        self.assertAlmostEqual(o.clock_angle_vec[0], 0, delta=0.2)
        self.assertAlmostEqual(o.clock_angle_vec[1], 180, delta=0.2)
        self.assertAlmostEqual(o.clock_angle_vec[2], 180, delta=0.2)
        self.assertAlmostEqual(o.clock_angle_vec[3], 360, delta=0.2)
        self.assertEqual(o.angle_height, 0.1)
        self.assertAlmostEqual(o.angle_width, 50)
        self.assertEqual(o._id, "123")

        # Test case with incomplete specification
        with self.assertRaises(Exception):
            SphericalGeometry.from_json(
                '{"shape": "RECTANGULAR", "angleHeight": 60 }')
        # Test for out-of-range specification
        with self.assertRaises(Exception):
            SphericalGeometry.from_json(
                '{"shape": "RECTANGULAR", "angleHeight": 30 , "angleWidth": 210}')
        with self.assertRaises(Exception):
            SphericalGeometry.from_json(
                '{"shape": "RECTANGULAR", "angleHeight": -10 , "angleWidth": 5}')
        with self.assertRaises(Exception):
            SphericalGeometry.from_json(
                '{"shape": "RECTANGULAR", "angleHeight": -1110 , "angleWidth": 50}')

    def test_get_rect_poly_specs_from_cone_clock_angles(self):        
        # Square case
        o = SphericalGeometry.from_json('{"shape": "RECTANGULAR", "angleHeight": 15 , "angleWidth": 15}')
        [angle_height, angle_width] = SphericalGeometry.get_rect_poly_specs_from_cone_clock_angles(o.cone_angle_vec, o.clock_angle_vec)
        self.assertAlmostEqual(angle_height, 15)
        self.assertAlmostEqual(angle_width, 15)
        
        # Test edge case with small along-track fov
        o = SphericalGeometry.from_json(
            '{"shape": "RECTANGULAR", "angleHeight": 0.1 , "angleWidth": 30}')
        self.assertIsInstance(o, SphericalGeometry)
        [angle_height, angle_width] = SphericalGeometry.get_rect_poly_specs_from_cone_clock_angles(o.cone_angle_vec, o.clock_angle_vec)
        self.assertAlmostEqual(angle_height, 0.1)
        self.assertAlmostEqual(angle_width, 30)

        o = SphericalGeometry.from_json(
            '{"shape": "CUSTOM", "customConeAnglesVector": [30,30,30,30] , "customClockAnglesVector": [20,160,200,-20]}')
        [angle_height, angle_width] = SphericalGeometry.get_rect_poly_specs_from_cone_clock_angles(o.cone_angle_vec, o.clock_angle_vec)
        self.assertAlmostEqual(angle_height, 19.693103879668154)
        self.assertAlmostEqual(angle_width, 56.96247656267892)

        # Check for cases when the input cone, clock do not correspond to a rectangular fov
        with self.assertRaises(Exception):
            o.get_rect_poly_specs_from_cone_clock_angles([20], None)
        with self.assertRaises(Exception):
            o.get_rect_poly_specs_from_cone_clock_angles([10,10,10,10], [30,60,180,220])
        # slight tweaking of cone, clock angles corresponding to valid rectangular shape (15 deg x 15 deg) 
        with self.assertRaises(Exception):
            o.get_rect_poly_specs_from_cone_clock_angles([10.591411134810208, 10.591411134810208, 10.591411134810208, 10.591411134810208],
                                                         [45.246138033024906, 134.75386196697508, 125.24613803302492, 314.7538619669751])
        with self.assertRaises(Exception):
            o.get_rect_poly_specs_from_cone_clock_angles([10.591411134810208, 10.591411134810208, 10.591411134810208, 10.591411134810208, 10.591411134810208], 
                                                         [45.246138033024906, 134.75386196697508, 225.24613803302492, 314.7538619669751])
        with self.assertRaises(Exception):
            o.get_rect_poly_specs_from_cone_clock_angles([10.591411134810208, 20.591411134810208, 10.591411134810208, 10.591411134810208], 
                                                         [45.246138033024906, 134.75386196697508, 225.24613803302492, 314.7538619669751])

    def test_to_dict(self):
        # custom shape
        o = SphericalGeometry.from_json(
            '{"shape": "CUSTOM", "customConeAnglesVector": [10,10,10,10] , "customClockAnglesVector": [30,60,180,220]}')
        d = o.to_dict()
        self.assertEqual(d["shape"], "CUSTOM")
        self.assertEqual(d["customConeAnglesVector"], "[10.0,10.0,10.0,10.0]")
        self.assertEqual(d["customClockAnglesVector"], "[30.0,60.0,180.0,220.0]")
        self.assertIsNone(d["@id"])
        # circular shape
        o = SphericalGeometry.from_json(
            '{"shape": "CIRCULAR", "diameter": 30, "@id": 123}')
        d = o.to_dict()
        self.assertEqual(d["shape"], "CIRCULAR")
        self.assertEqual(d["diameter"], 30.0)
        self.assertEqual(d["@id"], 123)
        
        # rectangular shape
        o = SphericalGeometry.from_json(
            '{"shape": "RECTANGULAR", "angleHeight": 10 , "angleWidth": 30, "@id": "123"}')
        d = o.to_dict()
        self.assertEqual(d["shape"], "RECTANGULAR")
        self.assertEqual(d["angleHeight"], 10.0)
        self.assertAlmostEqual(d["angleWidth"], 30.0)
        self.assertEqual(d["@id"], "123")

'''
class TestConstants(unittest.TestCase):
    def test_radiusOfEarthInKM(self):
        self.assertEqual(Constants.radiusOfEarthInKM, 6378.137)

    def test_speedOfLight(self):
        self.assertEqual(Constants.speedOfLight, 299792458)

    def test_Boltzmann(self):
        self.assertEqual(Constants.Boltzmann, 1.380649e-23)

    def test_angularSpeedofEarthInRADpS(self):
        self.assertAlmostEqual(
            Constants.angularSpeedofEarthInRADpS, 2*numpy.pi / 86400.0, places=5)

    def test_Planck(self):
        self.assertEqual(Constants.Planck, 6.62607015e-34)

    def test_SunBlackBodyTemperature(self):
        self.assertEqual(Constants.SunBlackBodyTemperature, 6000)





class TestMathUtilityFunctions(unittest.TestCase):

    @staticmethod
    def compute_satellite_footprint_speed_with_EF_vectors(_gmat_r_ef, _gmat_v_ef):
        """ GMAT does not directly output the ground-speed. Compute using EF position vector and EF velocity vector available from GMAT. 
            In this case no compensation needs to be performed for Earth-rotation (unlike in the case of instrupy.MathUtilityFunctions.compute_satellite_footprint_speed(r,v) 
            where the input vectors (r,v) are in ECI frame) since the (r,v) vectors are taken in EF frame. 

        """
        _gmat_omega = numpy.cross(
            _gmat_r_ef, _gmat_v_ef) / (numpy.linalg.norm(_gmat_r_ef)**2)
        _gmat_fp_speed = numpy.linalg.norm(_gmat_omega)*6378100
        return _gmat_fp_speed

    def test_compute_satellite_footprint_speed(self):

        # Validating using 'GMAT R2018a 64bit' as external reference.
        # Test 1 (low inclination orbit)
        _gmat_r_eci = [7100, 0, 1300]
        _gmat_v_eci = [0, 7.35, 1]
        _gmat_r_ef = [1272.929354832122, 6984.992046762509, 1299.821897134824]
        _gmat_v_ef = [-6.721571319063451,
                      1.224987254217343, 0.9997979087785365]
        _gmat_fp_speed = TestMathUtilityFunctions.compute_satellite_footprint_speed_with_EF_vectors(
            _gmat_r_ef, _gmat_v_ef)
        fp_speed = MathUtilityFunctions.compute_satellite_footprint_speed(
            _gmat_r_eci, _gmat_v_eci)
        # acceptable error limits of 10 m/s
        self.assertAlmostEqual(_gmat_fp_speed, fp_speed, delta=10)

        # Test 2 (mid inclination orbit)
        _gmat_r_eci = [-5436.533450168191, -
                       3053.079465330414, 3181.636343704307]
        _gmat_v_eci = [1.114632787950382, -
                       6.244419534847031, -4.087510077679621]
        _gmat_r_ef = [2028.820780817868, -5895.733640536318, 3181.856545975942]
        _gmat_v_ef = [5.913247918270616, -
                      0.1710549493218195, -4.087366758963451]
        _gmat_fp_speed = TestMathUtilityFunctions.compute_satellite_footprint_speed_with_EF_vectors(
            _gmat_r_ef, _gmat_v_ef)
        fp_speed = MathUtilityFunctions.compute_satellite_footprint_speed(
            _gmat_r_eci, _gmat_v_eci)
        # acceptable error limits of 10 m/s
        self.assertAlmostEqual(_gmat_fp_speed, fp_speed, delta=10)

        # Test (retrograde high inclination orbit)
        _gmat_r_eci = [-2138.840731205298, -
                       4957.003244328315, 4455.724313987103]
        _gmat_v_eci = [-3.12197717174031, -3.798411634168159, -5.7243556677441]
        _gmat_r_ef = [4493.108372866067, -
                      2992.792499467348,  4455.914070627137]
        _gmat_v_ef = [2.959015709181303, -
                      4.08021854816618,  -5.724173608651788]
        _gmat_fp_speed = TestMathUtilityFunctions.compute_satellite_footprint_speed_with_EF_vectors(
            _gmat_r_ef, _gmat_v_ef)
        fp_speed = MathUtilityFunctions.compute_satellite_footprint_speed(
            _gmat_r_eci, _gmat_v_eci)
        # acceptable error limits of 10 m/s
        self.assertAlmostEqual(_gmat_fp_speed, fp_speed, delta=10)

        # Test (retrograde mid-incinaton orbit)
        _gmat_r_eci = [74.22234833534203, -6234.715809034727, 3181.63634370431]
        _gmat_v_eci = [-5.965142343040525, -
                       2.15690945716741, -4.087510077679617]
        _gmat_r_ef = [6146.925885818154, -1044.708013320701,  3181.80566992428]
        _gmat_v_ef = [0.9763805839389828, -
                      6.703558863610055, -4.087302022035398]
        _gmat_fp_speed = TestMathUtilityFunctions.compute_satellite_footprint_speed_with_EF_vectors(
            _gmat_r_ef, _gmat_v_ef)
        fp_speed = MathUtilityFunctions.compute_satellite_footprint_speed(
            _gmat_r_eci, _gmat_v_eci)
        # acceptable error limits of 10 m/s
        self.assertAlmostEqual(_gmat_fp_speed, fp_speed, delta=10)

    def test_latlonalt_To_Cartesian(self):

        # Test, trivial case with point at (0 deg,0 deg,0 km)
        p_vec = MathUtilityFunctions.latlonalt_To_Cartesian(0, 0, 0)
        self.assertAlmostEqual(p_vec[0], 6378.137, delta=1)
        self.assertAlmostEqual(p_vec[1], 0)
        self.assertAlmostEqual(p_vec[2], 0)

        # Test, trivial case with point at (0 deg, 90 deg,0 km)
        p_vec = MathUtilityFunctions.latlonalt_To_Cartesian(0, 90, 0)
        self.assertAlmostEqual(p_vec[0], 0)
        self.assertAlmostEqual(p_vec[1], 6378.137, delta=1)
        self.assertAlmostEqual(p_vec[2], 0)

        # Test, trivial case with point at (0 deg, -90 deg,0 km)
        p_vec = MathUtilityFunctions.latlonalt_To_Cartesian(0, -90, 0)
        self.assertAlmostEqual(p_vec[0], 0)
        self.assertAlmostEqual(p_vec[1], -6378.137, delta=1)
        self.assertAlmostEqual(p_vec[2], 0)

        # Test, trivial case with point at (0 deg, -90 deg,100 km)
        p_vec = MathUtilityFunctions.latlonalt_To_Cartesian(0, -90, 100)
        self.assertAlmostEqual(p_vec[0], 0)
        self.assertAlmostEqual(p_vec[1], -6378.137 - 100, delta=1)
        self.assertAlmostEqual(p_vec[2], 0)

        # Test, trivial case with point at (90 deg, 90 deg,100 km)
        p_vec = MathUtilityFunctions.latlonalt_To_Cartesian(90, 90, 500)
        self.assertAlmostEqual(p_vec[0], 0)
        self.assertAlmostEqual(p_vec[1], 0)
        self.assertAlmostEqual(p_vec[2], 6378.137 + 500, delta=1)

        # Test, trivial case with point at (40 deg, 270 deg,100 km) and point at (40 deg, -90 deg,100 km) (both coords a off the same point)
        p_vec1 = MathUtilityFunctions.latlonalt_To_Cartesian(40, 270, 100)
        p_vec2 = MathUtilityFunctions.latlonalt_To_Cartesian(40, -90, 100)
        self.assertAlmostEqual(p_vec1[0], p_vec2[0])
        self.assertAlmostEqual(p_vec1[1], p_vec2[1])
        self.assertAlmostEqual(p_vec1[2], p_vec2[2])

    def test_latlonaltGeodetic_To_Cartesian(self):
        """ Validating using 'GMAT R2018a 64bit' as external reference.         
            Generate some latitude, longitude and corresponding [X,Y,Z] position (in EF frame) of a object in GMAT. 
            Check with the generated Cartesian position vector of the instrupy.MathUtilityFunctions.latlonalt_To_Cartesian(...).

        """
        # Test case 1, positive lat, positive lon
        p_vec = MathUtilityFunctions.latlonaltGeodetic_To_Cartesian(
            65.8772312763883,  102.0971826243001, 643.382903131308)
        _gmat_p_vec = [-602.9227650102, 2813.05830480065, 6385.563708800454]
        # acceptable error limits of 1 km
        self.assertAlmostEqual(p_vec[0], _gmat_p_vec[0], delta=1)
        self.assertAlmostEqual(p_vec[1], _gmat_p_vec[1], delta=1)
        self.assertAlmostEqual(p_vec[2], _gmat_p_vec[2], delta=1)

        # Test case 2, positive lat, negative lon
        p_vec = MathUtilityFunctions.latlonaltGeodetic_To_Cartesian(
            39.70771912759876, -33.66699237384308, 630.5515018592132)
        _gmat_p_vec = [4493.108372866067, -
                       2992.792499467348, 4455.914070627137]
        # acceptable error limits of 1 km
        self.assertAlmostEqual(p_vec[0], _gmat_p_vec[0], delta=1)
        self.assertAlmostEqual(p_vec[1], _gmat_p_vec[1], delta=1)
        self.assertAlmostEqual(p_vec[2], _gmat_p_vec[2], delta=1)

        # Test case 3, negative lat, positive lon
        p_vec = MathUtilityFunctions.latlonaltGeodetic_To_Cartesian(
            -15.57990628688177, 128.1073197882878,  631.6338423255838)
        _gmat_p_vec = [-4167.949699384632,
                       5314.18497094466, -1871.641779273967]
        # acceptable error limits of 1 km
        self.assertAlmostEqual(p_vec[0], _gmat_p_vec[0], delta=1)
        self.assertAlmostEqual(p_vec[1], _gmat_p_vec[1], delta=1)
        self.assertAlmostEqual(p_vec[2], _gmat_p_vec[2], delta=1)

        # Test case 4, negative lat, negative lon
        p_vec = MathUtilityFunctions.latlonaltGeodetic_To_Cartesian(
            -68.9408803669571,  -93.36510673726006,  640.3777836151294)
        _gmat_p_vec = [-148.4295520342744, -
                       2524.319956760156, -6527.213550924283]
        # acceptable error limits of 1 km
        self.assertAlmostEqual(p_vec[0], _gmat_p_vec[0], delta=1)
        self.assertAlmostEqual(p_vec[1], _gmat_p_vec[1], delta=1)
        self.assertAlmostEqual(p_vec[2], _gmat_p_vec[2], delta=1)

    def test_geo2eci(self):
        """ Truth data from `IDL Astronomy Users Library <https://idlastro.gsfc.nasa.gov/ftp/pro/astro/geo2eci.pro>`_, on which the 
            python function being tested is also written.
        """
        # intersection of the equator and Greenwich's meridian on 2002/03/09 21:21:21.021
        sample = MathUtilityFunctions.geo2eci([0, 0, 0], 2452343.38982663)
        truth = [-3902.9606, 5044.5548, 0.0000000]
        self.assertAlmostEqual(sample[0], truth[0], places=3)
        self.assertAlmostEqual(sample[1], truth[1], places=3)
        self.assertAlmostEqual(sample[2], truth[2], places=3)

    def test_compute_sun_zenith(self):
        """ Truth data from https://www.esrl.noaa.gov/gmd/grad/solcalc/
        """

        time_JDUT1 = 2452343.38982663  # 2002/03/09 21:21:21.021
        pos_km = MathUtilityFunctions.geo2eci([0.0,  0.0, 0.0], time_JDUT1)
        self.assertIsNone(MathUtilityFunctions.compute_sun_zenith(
            time_JDUT1, pos_km)[0])  # cause it is night

        time_JDUT1 = 2452343.000000  # 2002/03/09 12:00:00.000
        pos_km = MathUtilityFunctions.geo2eci([0.0,  0.0, 0.0], time_JDUT1)
        self.assertAlmostEqual(MathUtilityFunctions.compute_sun_zenith(
            time_JDUT1, pos_km)[0], numpy.deg2rad(90-84.82), places=2)

        time_JDUT1 = 2458619.133333  # A.D. 2019 May 15 15:12:00.0
        pos_km = MathUtilityFunctions.geo2eci(
            [61.217,  -149.9, 0.0], time_JDUT1)
        self.assertAlmostEqual(MathUtilityFunctions.compute_sun_zenith(
            time_JDUT1, pos_km)[0], numpy.deg2rad(90-11.44), places=2)

    def test_normalize(self):

        # Test if returned vector has unit magnitude
        self.assertAlmostEqual(numpy.linalg.norm(
            MathUtilityFunctions.normalize([2, 4, 6])), 1)
        self.assertAlmostEqual(numpy.linalg.norm(
            MathUtilityFunctions.normalize([-2, 4, 65])), 1)
        self.assertAlmostEqual(numpy.linalg.norm(
            MathUtilityFunctions.normalize([2, 0, 0])), 1)
        self.assertAlmostEqual(numpy.linalg.norm(
            MathUtilityFunctions.normalize([2, -4, -42343])), 1)

        with self.assertRaises(Exception):
            MathUtilityFunctions.normalize([0, 0, 0])

    def test_angle_between_vectors(self):

        # Test trivial cases
        self.assertAlmostEqual(MathUtilityFunctions.angle_between_vectors(
            [100, 0, 0], [0, 1, 0]), numpy.pi/2)
        self.assertAlmostEqual(MathUtilityFunctions.angle_between_vectors(
            [100, 0, 0], [-5000, 0, 0]), numpy.pi)
        self.assertAlmostEqual(MathUtilityFunctions.angle_between_vectors(
            [45, 45, 45], [-45, -45, -45]), numpy.pi)
        self.assertAlmostEqual(MathUtilityFunctions.angle_between_vectors(
            [45, 45, 45], [45, 45, 45]), 0)
        self.assertAlmostEqual(MathUtilityFunctions.angle_between_vectors(
            [.5, .5, 0], [1, 0, 0]), numpy.pi/4)

    def test_JD2GMST(self):
        """ Truth data is from David A. Vallado,"Fundamentals of Astrodynamics and Applications", 4th ed, page after index titled julian Data Values.
            The table gives the GMST in degrees, hence is converted into hours for testing the intrupy.MathUtilityFunctions.JD2GMST(...) function.
            Note that in the table the JD is specified at 12h UT, while GMST is at 0h UT. Take this into account.
            For example, for the date 2000 Jan 1 12h UT, the table reads the JD as 2451545. Since the GMST is specified at 0h UT (on the same day), the corresponding
            JD to be input is 2451544.5, corresponding to the date 2000 Jan 1 0h UT.
        """
        self.assertAlmostEqual(MathUtilityFunctions.JD2GMST(
            2451544.5), 99.9677947 * (24/360), places=3)  # row corresponding to year 2000

        self.assertAlmostEqual(MathUtilityFunctions.JD2GMST(
            2415020.5), 100.1837764 * (24/360), places=3)  # row corresponding to year 1900
        self.assertAlmostEqual(MathUtilityFunctions.JD2GMST(
            2458119.5), 100.5992406 * (24/360), places=3)  # row corresponding to year 2018
        self.assertAlmostEqual(MathUtilityFunctions.JD2GMST(
            2466154.5), 100.2728782 * (24/360), places=3)  # row corresponding to year 2040 (Leap year)

        """ Truth data from https://www.celnav.de/longterm.htm.

        """
        self.assertAlmostEqual(MathUtilityFunctions.JD2GMST(
            2458542.127859), 1.5460, places=3)  # 2019/02/27 15:04:07 UT, after 12h UT test
        self.assertAlmostEqual(MathUtilityFunctions.JD2GMST(
            2459823.582662), 0.665478055555556, places=3)  # 2022/09/01 01:59:02 UT, before 12h UT test

    def test_find_closest_value_in_array(self):

        self.assertEqual(MathUtilityFunctions.find_closest_value_in_array(
            [10, 45, 3, -10], 9), [10, 0])
        self.assertEqual(MathUtilityFunctions.find_closest_value_in_array(
            [10, 45, 3, -10], 25), [10, 0])
        self.assertEqual(MathUtilityFunctions.find_closest_value_in_array(
            [10, 45, 3, -10], 0), [3, 2])

    def test_SunVector_ECIeq(self):
        """ Truth data from running Matlab script :code:`sun.m` to compute Sun vector available as companion to 
            David A.Vallado, Fundamental of Astrodynamics and Applications, 4th ed.
            Acceptable deviation is kept as 0.1km.
        """
        # A.D. 2006 Apr 2, 0 UT1
        self.assertAlmostEqual(MathUtilityFunctions.SunVector_ECIeq(
            2453827.5)[0], 146186212.986846, delta=0.1)
        self.assertAlmostEqual(MathUtilityFunctions.SunVector_ECIeq(
            2453827.5)[1], 28788976.3117029, delta=0.1)
        self.assertAlmostEqual(MathUtilityFunctions.SunVector_ECIeq(
            2453827.5)[2], 	12481063.6450839, delta=0.1)

        # A.D. 2019 Feb 27, 15:56:00.0 UT1
        self.assertAlmostEqual(MathUtilityFunctions.SunVector_ECIeq(
            2458542.163889)[0], 138092570.424158, delta=0.1)
        self.assertAlmostEqual(MathUtilityFunctions.SunVector_ECIeq(
            2458542.163889)[1], -49238069.9169012, delta=0.1)
        self.assertAlmostEqual(MathUtilityFunctions.SunVector_ECIeq(
            2458542.163889)[2],	-21344772.5319679, delta=0.1)

    def test_checkLOSavailability(self):
        """ Truth data from running Matlab script :code:`sight.m` to compute SUn vector available as companion to 
            David A.Vallado, Fundamental of Astrodynamics and Applications, 4th ed.           
        """
        self.assertFalse(MathUtilityFunctions.checkLOSavailability(
            [-4464.696, -5102.509, 0], [5740.323, 3189.068, 0], 6378.137))
        self.assertTrue(MathUtilityFunctions.checkLOSavailability(
            [-4464.696, -5102.509, 0], [-4464.696, -5102.509, 100], 6378.137))
        self.assertTrue(MathUtilityFunctions.checkLOSavailability(
            [-4464.696, -5102.509, 0], [-7464.696, 102.509, 100], 6378.137))

    def test_calculate_derived_satellite_coords(self):

        # Test for cases where the input satellite position, time is equal to derived satellite position, time

        tObs_JDUT1 = 100.0
        obs_position_km = [6378+700, 0, 0]
        obs_vel_vec_kmps = [0, 6.5, 0]
        target_position_km = [6378, 0, 0]
        derived_coords = MathUtilityFunctions.calculate_derived_satellite_coords(
            tObs_JDUT1, obs_position_km, obs_vel_vec_kmps, target_position_km)
        self.assertEqual(derived_coords["derived_obsTime_JDUT1"], 100)
        self.assertEqual(
            derived_coords["derived_obs_pos_km"], [6378+700, 0, 0])
        self.assertEqual(derived_coords["derived_range_vec_km"], [-700, 0, 0])
        self.assertAlmostEqual(derived_coords["derived_alt_km"], 700, delta=1)
        self.assertEqual(derived_coords["derived_incidence_angle_rad"], 0)

        tObs_JDUT1 = 100.0
        obs_position_km = [6378+700, 100, 0]
        obs_vel_vec_kmps = [0, 6.5, 0]
        target_position_km = [6378, 100, 0]
        derived_coords = MathUtilityFunctions.calculate_derived_satellite_coords(
            tObs_JDUT1, obs_position_km, obs_vel_vec_kmps, target_position_km)
        self.assertEqual(derived_coords["derived_obsTime_JDUT1"], 100)
        self.assertEqual(derived_coords["derived_obs_pos_km"], [
                         6378+700, 100, 0])
        self.assertEqual(derived_coords["derived_range_vec_km"], [-700, 0, 0])
        self.assertAlmostEqual(derived_coords["derived_alt_km"], 700, delta=1)
        self.assertEqual(
            derived_coords["derived_incidence_angle_rad"], 0.015679201843266006)

        tObs_JDUT1 = 100.0
        obs_position_km = [6378+700, 0, 0]
        obs_vel_vec_kmps = [0, -6.5, 0]
        target_position_km = [6378, 0, 0]
        derived_coords = MathUtilityFunctions.calculate_derived_satellite_coords(
            tObs_JDUT1, obs_position_km, obs_vel_vec_kmps, target_position_km)
        self.assertEqual(derived_coords["derived_obsTime_JDUT1"], 100)
        self.assertEqual(
            derived_coords["derived_obs_pos_km"], [6378+700, 0, 0])
        self.assertEqual(derived_coords["derived_range_vec_km"], [-700, 0, 0])
        self.assertAlmostEqual(derived_coords["derived_alt_km"], 700, delta=1)
        self.assertEqual(derived_coords["derived_incidence_angle_rad"], 0)

        tObs_JDUT1 = 100.0
        obs_position_km = [6378+700, 0, 0]
        obs_vel_vec_kmps = [0, -6.5, 0]
        target_position_km = [6378, 0, 100]
        derived_coords = MathUtilityFunctions.calculate_derived_satellite_coords(
            tObs_JDUT1, obs_position_km, obs_vel_vec_kmps, target_position_km)
        self.assertEqual(derived_coords["derived_obsTime_JDUT1"], 100)
        self.assertEqual(
            derived_coords["derived_obs_pos_km"], [6378+700, 0, 0])
        self.assertEqual(
            derived_coords["derived_range_vec_km"], [-700, 0, 100])
        self.assertAlmostEqual(derived_coords["derived_alt_km"], 700, delta=1)
        self.assertAlmostEqual(derived_coords["derived_incidence_angle_rad"], (numpy.arcsin(numpy.arctan2(
            100, 700) * (6378+700)/6378.137)), places=2)  # note that look angle of truth data is approximate

        # Test for cases where the input satellite position, time is different from derived satellite position, time

        tObs_JDUT1 = 100.0
        obs_position_km = [6378+700, 0, 0]
        obs_vel_vec_kmps = [0, 6.5, 0]
        target_position_km = [6378, 6.5, 0]
        derived_coords = MathUtilityFunctions.calculate_derived_satellite_coords(
            tObs_JDUT1, obs_position_km, obs_vel_vec_kmps, target_position_km)
        self.assertEqual(derived_coords["derived_obsTime_JDUT1"], 101)
        self.assertEqual(derived_coords["derived_obs_pos_km"], [
                         6378+700, 6.5, 0])
        self.assertEqual(derived_coords["derived_range_vec_km"], [-700, 0, 0])
        self.assertAlmostEqual(derived_coords["derived_alt_km"], 700, delta=1)
        # approximate truth data since Earth curvature is ignored
        self.assertAlmostEqual(
            derived_coords["derived_incidence_angle_rad"], 0, places=2)

        tObs_JDUT1 = 100.0
        obs_position_km = [6378+700, 0, 0]
        obs_vel_vec_kmps = [0, 6.5, 0]
        target_position_km = [6378, 13.0, 100]
        derived_coords = MathUtilityFunctions.calculate_derived_satellite_coords(
            tObs_JDUT1, obs_position_km, obs_vel_vec_kmps, target_position_km)
        self.assertEqual(derived_coords["derived_obsTime_JDUT1"], 102)
        self.assertEqual(derived_coords["derived_obs_pos_km"], [
                         6378+700, 13.0, 0])
        self.assertEqual(
            derived_coords["derived_range_vec_km"], [-700, 0, 100])
        self.assertAlmostEqual(derived_coords["derived_alt_km"], 700, delta=1)
        self.assertAlmostEqual(derived_coords["derived_incidence_angle_rad"], (numpy.arcsin(
            numpy.arctan2(100, 700) * (6378+700)/6378.137)), places=2)


class TestFileUtilityFunctions(unittest.TestCase):
    def test_from_json(self):

        # Test empty JSON string
        o = FileUtilityFunctions.from_json('{}')
        self.assertEqual(o, {})

        # Test one string field
        o = FileUtilityFunctions.from_json('{"name": "Maple"}')
        self.assertEqual(o["name"], "Maple")
        self.assertIsInstance(o["name"],  str)

        # Test erroneous JSON format
        with self.assertRaises(Exception):
            FileUtilityFunctions.from_json('{"name": }')

        # Test two string fields
        o = FileUtilityFunctions.from_json(
            '{"name": "Maple", "@type": "Syrup"}')
        self.assertEqual(o["name"], "Maple")
        self.assertEqual(o["@type"], "Syrup")

        # Test two string fields, one number field
        o = FileUtilityFunctions.from_json(
            '{"name": "Maple", "@type": "Syrup", "volume": 10.4}')
        self.assertEqual(o["name"], "Maple")
        self.assertEqual(o["@type"], "Syrup")
        self.assertEqual(o["volume"],  10.4)
        self.assertIsInstance(o["volume"],  float)

        # Test two string fields, one number field, one list (str) field
        o = FileUtilityFunctions.from_json(
            '{"name": "Maple", "@type": "Syrup", "volume": 10.4, "places": ["CA","TX","WA"]}')
        self.assertEqual(o["name"], "Maple")
        self.assertEqual(o["@type"], "Syrup")
        self.assertEqual(o["volume"],  10.4)
        self.assertEqual(o["places"],  ["CA", "TX", "WA"])
        self.assertIsInstance(o["places"],  list)

        # Test two string fields, one number field, one list (value) field
        o = FileUtilityFunctions.from_json(
            '{"name": "Maple", "@type": "Syrup", "volume": 10.4, "batches": [2011,2018,2023]}')
        self.assertEqual(o["name"], "Maple")
        self.assertEqual(o["@type"], "Syrup")
        self.assertEqual(o["volume"],  10.4)
        self.assertEqual(o["batches"],  [2011, 2018, 2023])
        self.assertIsInstance(o["batches"],  list)

        # Test passing of a dictionary
        data = {'name': 'Maple', '@type': 'Syrup',
                'batches': [2011, 2018, 2023]}
        o = FileUtilityFunctions.from_json(data)
        self.assertEqual(o["name"], "Maple")
        self.assertEqual(o["@type"], "Syrup")
        self.assertEqual(o["batches"],  [2011, 2018, 2023])

        # Test nested json fields
        o = FileUtilityFunctions.from_json(
            '{"name": "Maple", "@type": "Syrup", "volume": 10.4, "nutrition": { "Fat": 0, "Sodium": 2, "Protein": 0}}')
        self.assertEqual(o["name"], "Maple")
        self.assertEqual(o["@type"], "Syrup")
        self.assertEqual(o["nutrition"],  {
                         'Fat': 0, 'Sodium': 2, 'Protein': 0})
        self.assertEqual(o["nutrition"]["Fat"],  0)
'''