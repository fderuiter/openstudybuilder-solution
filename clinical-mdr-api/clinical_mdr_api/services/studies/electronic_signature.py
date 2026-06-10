import datetime
from uuid import uuid4

from neomodel import db

from clinical_mdr_api.models.study_selections.electronic_signature import (
    ElectronicSignatureCreateInput,
    ElectronicSignatureResponse,
)
from common.exceptions import BusinessLogicException

def sign_study_selection(
    user_id: str,
    study_selection_uid: str,
    input_data: ElectronicSignatureCreateInput,
) -> ElectronicSignatureResponse:
    # 1. Fetch the state (StudySelection)
    query = """
    MATCH (ss:StudySelection {uid: $study_selection_uid})
    OPTIONAL MATCH (ss)<-[:BEFORE]-(sa:StudyAction)
    OPTIONAL MATCH (ss)<-[:AFTER]-(sa_after:StudyAction)
    RETURN ss, sa, sa_after
    """
    results, _ = db.cypher_query(query, {"study_selection_uid": study_selection_uid})
    
    if not results:
        raise BusinessLogicException(f"Study selection with uid {study_selection_uid} not found", status_code=404)
        
    row = results[0]
    ss_node = row[0]
    sa_node = row[1]
    sa_after_node = row[2]
    
    if sa_node is not None:
        raise BusinessLogicException("Cannot sign a version that has already been superseded.", status_code=400)
        
    # The signature timestamp must be >= StudyAction timestamp
    if sa_after_node:
        if hasattr(sa_after_node, "get"):
            sa_after_date = sa_after_node.get("date")
        else:
            sa_after_date = getattr(sa_after_node, "date", None)
    else:
        sa_after_date = None
        
    current_time = datetime.datetime.now(datetime.timezone.utc)
    if sa_after_date and current_time < sa_after_date:
        current_time = sa_after_date
    
    # Update status to 'Signed'
    update_query = """
    MATCH (ss:StudySelection {uid: $study_selection_uid})
    SET ss.status = 'Signed'
    """
    db.cypher_query(update_query, {"study_selection_uid": study_selection_uid})
    
    # Create ElectronicSignature node
    sig_uid = str(uuid4())
    create_query = """
    CREATE (es:ElectronicSignature {
        uid: $sig_uid,
        date: $date,
        author_id: $author_id,
        meaning_of_signature: $meaning_of_signature
    })
    RETURN es
    """
    db.cypher_query(create_query, {
        "sig_uid": sig_uid,
        "date": current_time,
        "author_id": user_id,
        "meaning_of_signature": input_data.meaning_of_signature
    })
    
    # Link it to the state via AFTER relationship and directly to the StudyAction that created the state
    if sa_after_node:
        link_query = """
        MATCH (es:ElectronicSignature {uid: $sig_uid})
        MATCH (ss:StudySelection {uid: $study_selection_uid})
        MATCH (sa:StudyAction) WHERE id(sa) = $sa_id
        MERGE (es)-[:AFTER]->(ss)
        MERGE (es)-[:SIGNS]->(sa)
        """
        db.cypher_query(link_query, {
            "sig_uid": sig_uid,
            "study_selection_uid": study_selection_uid,
            "sa_id": sa_after_node.element_id if hasattr(sa_after_node, 'element_id') else sa_after_node.id
        })
        
    return ElectronicSignatureResponse(
        uid=sig_uid,
        date=current_time,
        author_id=user_id,
        meaning_of_signature=input_data.meaning_of_signature,
        signed_node_uid=study_selection_uid
    )
