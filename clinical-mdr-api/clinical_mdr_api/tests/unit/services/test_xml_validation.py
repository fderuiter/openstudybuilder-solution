import pytest
from unittest.mock import MagicMock, patch
from dataclasses import dataclass
from typing import Any
from xml.dom.minidom import Document

from clinical_mdr_api.domains.odms.utils import TargetType
from clinical_mdr_api.services.odms.xml_exporter import OdmXmlExporterService
from common.exceptions import ValidationException

@dataclass
class MockNamespaceSimple:
    prefix: str
    url: str
    uid: str = "ns-1"
    name: str = "Test Namespace"

@dataclass
class MockElementSimple:
    uid: str
    name: str

@dataclass
class MockVendorElement:
    uid: str
    name: str
    compatible_types: list[str]
    vendor_namespace: Any

@dataclass
class MockVendorAttribute:
    uid: str
    name: str
    compatible_types: list[str] = None
    data_type: str = "string"
    value_regex: str = None
    vendor_namespace: Any = None
    vendor_element: Any = None

class GenericReturn:
    def __init__(self, items):
        self.items = items

def test_xml_validation_success():
    # 1. Prepare active database vendor metadata models (mocked)
    ns = MockNamespaceSimple(prefix="clinical", url="http://clinical.org", uid="ns-1")
    
    elem1 = MockVendorElement(
        uid="elem-1",
        name="customElement",
        compatible_types=["FormDef", "ItemGroupDef"],
        vendor_namespace=ns
    )
    
    attr1 = MockVendorAttribute(
        uid="attr-1",
        name="customAttr",
        compatible_types=["FormDef"],
        vendor_namespace=ns
    )
    
    attr2 = MockVendorAttribute(
        uid="attr-2",
        name="elementAttr",
        vendor_element=MockElementSimple(uid="elem-1", name="customElement"),
        value_regex="^[0-9]+$"
    )

    with patch("clinical_mdr_api.services.odms.xml_exporter.OdmDataExtractor") as MockExtractor:
        # Configure the extractor mock
        extractor = MockExtractor.return_value
        extractor.odm_vendor_namespaces = {"ns-1": {"prefix": "clinical", "url": "http://clinical.org", "name": "Test"}}
        
        # Setup mock return values for services
        extractor.vendor_namespace_service.get_all_odms.return_value = GenericReturn([ns])
        extractor.vendor_element_service.get_all_odms.return_value = GenericReturn([elem1])
        extractor.vendor_attribute_service.get_all_odms.return_value = GenericReturn([attr1, attr2])

        # Instantiate exporter
        exporter = OdmXmlExporterService(
            target_type=TargetType.FORM,
            targets=["form-1,1"],
            allowed_namespaces=["clinical"],
            pdf=False,
            stylesheet=None,
            mapper_file=None
        )

        # Let's mock xml_document directly
        doc = Document()
        root = doc.createElement("ODM")
        doc.appendChild(root)
        
        # Add standard FormDef
        form = doc.createElement("FormDef")
        root.appendChild(form)
        
        # Add valid custom vendor attribute on FormDef
        form.setAttribute("clinical:customAttr", "someValue")
        
        # Add valid custom vendor element under FormDef
        cust_elem = doc.createElement("clinical:customElement")
        form.appendChild(cust_elem)
        
        # Add valid custom element attribute with matching value regex
        cust_elem.setAttribute("clinical:elementAttr", "12345")
        
        exporter.xml_document = doc
        
        # Validation should succeed without raising any exceptions!
        exporter.validate_xml_structure()


def test_xml_validation_undeclared_element():
    ns = MockNamespaceSimple(prefix="clinical", url="http://clinical.org", uid="ns-1")
    
    with patch("clinical_mdr_api.services.odms.xml_exporter.OdmDataExtractor") as MockExtractor:
        extractor = MockExtractor.return_value
        extractor.odm_vendor_namespaces = {"ns-1": {"prefix": "clinical", "url": "http://clinical.org", "name": "Test"}}
        extractor.vendor_namespace_service.get_all_odms.return_value = GenericReturn([ns])
        extractor.vendor_element_service.get_all_odms.return_value = GenericReturn([])
        extractor.vendor_attribute_service.get_all_odms.return_value = GenericReturn([])

        exporter = OdmXmlExporterService(
            target_type=TargetType.FORM,
            targets=["form-1,1"],
            allowed_namespaces=["clinical"],
            pdf=False,
            stylesheet=None,
            mapper_file=None
        )

        doc = Document()
        root = doc.createElement("ODM")
        doc.appendChild(root)
        form = doc.createElement("FormDef")
        root.appendChild(form)
        
        # Add undeclared custom vendor element
        cust_elem = doc.createElement("clinical:unregisteredElement")
        form.appendChild(cust_elem)
        
        exporter.xml_document = doc
        
        with pytest.raises(ValidationException) as exc_info:
            exporter.validate_xml_structure()
            
        assert "unregisteredElement" in str(exc_info.value)
        assert "is not declared in the database" in str(exc_info.value)


def test_xml_validation_incompatible_element_parent():
    ns = MockNamespaceSimple(prefix="clinical", url="http://clinical.org", uid="ns-1")
    elem1 = MockVendorElement(
        uid="elem-1",
        name="customElement",
        compatible_types=["FormDef"],  # Only allowed under FormDef
        vendor_namespace=ns
    )
    
    with patch("clinical_mdr_api.services.odms.xml_exporter.OdmDataExtractor") as MockExtractor:
        extractor = MockExtractor.return_value
        extractor.odm_vendor_namespaces = {"ns-1": {"prefix": "clinical", "url": "http://clinical.org", "name": "Test"}}
        extractor.vendor_namespace_service.get_all_odms.return_value = GenericReturn([ns])
        extractor.vendor_element_service.get_all_odms.return_value = GenericReturn([elem1])
        extractor.vendor_attribute_service.get_all_odms.return_value = GenericReturn([])

        exporter = OdmXmlExporterService(
            target_type=TargetType.FORM,
            targets=["form-1,1"],
            allowed_namespaces=["clinical"],
            pdf=False,
            stylesheet=None,
            mapper_file=None
        )

        doc = Document()
        root = doc.createElement("ODM")
        doc.appendChild(root)
        
        # Incompatible parent: ItemDef (not FormDef)
        item = doc.createElement("ItemDef")
        root.appendChild(item)
        cust_elem = doc.createElement("clinical:customElement")
        item.appendChild(cust_elem)
        
        exporter.xml_document = doc
        
        with pytest.raises(ValidationException) as exc_info:
            exporter.validate_xml_structure()
            
        assert "is not compatible with parent element <ItemDef>" in str(exc_info.value)


def test_xml_validation_incompatible_attribute_parent():
    ns = MockNamespaceSimple(prefix="clinical", url="http://clinical.org", uid="ns-1")
    attr1 = MockVendorAttribute(
        uid="attr-1",
        name="customAttr",
        compatible_types=["FormDef"],  # Only allowed on FormDef
        vendor_namespace=ns
    )
    
    with patch("clinical_mdr_api.services.odms.xml_exporter.OdmDataExtractor") as MockExtractor:
        extractor = MockExtractor.return_value
        extractor.odm_vendor_namespaces = {"ns-1": {"prefix": "clinical", "url": "http://clinical.org", "name": "Test"}}
        extractor.vendor_namespace_service.get_all_odms.return_value = GenericReturn([ns])
        extractor.vendor_element_service.get_all_odms.return_value = GenericReturn([])
        extractor.vendor_attribute_service.get_all_odms.return_value = GenericReturn([attr1])

        exporter = OdmXmlExporterService(
            target_type=TargetType.FORM,
            targets=["form-1,1"],
            allowed_namespaces=["clinical"],
            pdf=False,
            stylesheet=None,
            mapper_file=None
        )

        doc = Document()
        root = doc.createElement("ODM")
        doc.appendChild(root)
        
        # Incompatible parent: ItemDef (not FormDef)
        item = doc.createElement("ItemDef")
        root.appendChild(item)
        item.setAttribute("clinical:customAttr", "val")
        
        exporter.xml_document = doc
        
        with pytest.raises(ValidationException) as exc_info:
            exporter.validate_xml_structure()
            
        assert "is not compatible with element <ItemDef>" in str(exc_info.value)


def test_xml_validation_attribute_value_regex_mismatch():
    ns = MockNamespaceSimple(prefix="clinical", url="http://clinical.org", uid="ns-1")
    attr1 = MockVendorAttribute(
        uid="attr-1",
        name="numAttr",
        compatible_types=["FormDef"],
        value_regex="^[0-9]+$",  # must be numeric
        vendor_namespace=ns
    )
    
    with patch("clinical_mdr_api.services.odms.xml_exporter.OdmDataExtractor") as MockExtractor:
        extractor = MockExtractor.return_value
        extractor.odm_vendor_namespaces = {"ns-1": {"prefix": "clinical", "url": "http://clinical.org", "name": "Test"}}
        extractor.vendor_namespace_service.get_all_odms.return_value = GenericReturn([ns])
        extractor.vendor_element_service.get_all_odms.return_value = GenericReturn([])
        extractor.vendor_attribute_service.get_all_odms.return_value = GenericReturn([attr1])

        exporter = OdmXmlExporterService(
            target_type=TargetType.FORM,
            targets=["form-1,1"],
            allowed_namespaces=["clinical"],
            pdf=False,
            stylesheet=None,
            mapper_file=None
        )

        doc = Document()
        root = doc.createElement("ODM")
        doc.appendChild(root)
        form = doc.createElement("FormDef")
        root.appendChild(form)
        
        # Invalid value: abc (non-numeric)
        form.setAttribute("clinical:numAttr", "abc")
        
        exporter.xml_document = doc
        
        with pytest.raises(ValidationException) as exc_info:
            exporter.validate_xml_structure()
            
        assert "does not match pattern" in str(exc_info.value)
        assert "abc" in str(exc_info.value)


def test_xml_validation_performance_limit():
    # Verify that traversing/validating the tree runs extremely fast (<150ms target)
    ns = MockNamespaceSimple(prefix="clinical", url="http://clinical.org", uid="ns-1")
    elem1 = MockVendorElement(
        uid="elem-1",
        name="customElement",
        compatible_types=["FormDef"],
        vendor_namespace=ns
    )
    
    with patch("clinical_mdr_api.services.odms.xml_exporter.OdmDataExtractor") as MockExtractor:
        extractor = MockExtractor.return_value
        extractor.odm_vendor_namespaces = {"ns-1": {"prefix": "clinical", "url": "http://clinical.org", "name": "Test"}}
        extractor.vendor_namespace_service.get_all_odms.return_value = GenericReturn([ns])
        extractor.vendor_element_service.get_all_odms.return_value = GenericReturn([elem1])
        extractor.vendor_attribute_service.get_all_odms.return_value = GenericReturn([])

        exporter = OdmXmlExporterService(
            target_type=TargetType.FORM,
            targets=["form-1,1"],
            allowed_namespaces=["clinical"],
            pdf=False,
            stylesheet=None,
            mapper_file=None
        )

        doc = Document()
        root = doc.createElement("ODM")
        doc.appendChild(root)
        
        # Generate 100 deep/wide elements to check execution overhead
        for i in range(100):
            form = doc.createElement("FormDef")
            root.appendChild(form)
            cust_elem = doc.createElement("clinical:customElement")
            form.appendChild(cust_elem)
            
        exporter.xml_document = doc
        
        import time
        start = time.time()
        exporter.validate_xml_structure()
        end = time.time()
        
        elapsed_ms = (end - start) * 1000
        # Target limit is < 150ms. Standard DOM traversal for 200 nodes is typically < 2ms.
        assert elapsed_ms < 150
