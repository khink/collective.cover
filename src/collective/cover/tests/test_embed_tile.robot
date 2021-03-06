*** Settings ***

Resource  cover.robot
Library  Remote  ${PLONE_URL}/RobotRemote

Suite Setup  Open Test Browser
Suite Teardown  Close all browsers

*** Variables ***

${embed_tile_location}  'collective.cover.embed'
${embed_selector}  ul#item-list li.ui-draggable
${tile_selector}  div.tile-container div.tile
${title_field_id}  collective-cover-embed-title
${title_sample}  Some text for title
${title_other_sample}  This text should never be saved
${edit_link_selector}  a.edit-tile-link

*** Test cases ***

Test Embed Tile
    Enable Autologin as  Site Administrator
    Go to Homepage

    Create Cover  Title  Description  Empty layout
    Click Link  link=Layout

    Add Tile  ${embed_tile_location}
    Save Cover Layout

    Click Link  link=Compose
    Page Should Contain  Please edit the tile to add the code to be embedded.

    # edit header
    Click Link  link=Compose
    Click Link  css=${edit_link_selector}
    Wait until page contains element  id=${title_field_id}
    Input Text  id=${title_field_id}  ${title_sample}
    Click Button  Save
    # save via ajax => wait until the tile has been reloaded
    Wait Until Page Contains  ${title_sample}

    # edit tile but don't save it
    Click Link  css=${edit_link_selector}
    Wait until page contains element  id=${title_field_id}
    Input Text  id=${title_field_id}  ${title_other_sample}
    Click Button  Cancel
    Page Should Not Contain  ${title_other_sample}
    Page Should Contain  ${title_sample}

    Click Element  css=div#contentchooser-content-show-button

    # FIXME: current selectors suck!
    #Drag And Drop  css=${embed_selector}  css=${tile_selector}
    #Page Should Contain  The embed don't have any results

    Click Link  link=Layout
    Delete Tile
    Save Cover Layout
