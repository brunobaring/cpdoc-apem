from doc import Doc
from intro import intro_message
from helpers import sleep, make_request



keyword = input(intro_message())



def main():
    doc = Doc()



    # LOOPING THROUGH PAGINATION
    page = 13
    while True:



        # PREPARING URL AND REQUEST FOR RESULTS PAGES
        print(f'PAGE: {page}', flush=True)
        url = f"https://www6g.senado.gov.br/apem/search?keyword='{keyword}';startDoc={(page - 1) * 20 + 1}"
        main_response = make_request(url)



        if main_response.status_code != 200:
            break



        item_start_index = 0
        main_source = main_response.text



        # FETCHING OCCURRENCES COUNT
        occurrences_count_start_reference = '<span id="itemCount">'
        occurrences_count_start_index = main_source.find(occurrences_count_start_reference, item_start_index) + len(occurrences_count_start_reference)
        occurrences_count_end_reference = '</span>'
        occurrences_count_end_index = main_source.find(occurrences_count_end_reference, occurrences_count_start_index)
        occurrences_count = main_source[occurrences_count_start_index:occurrences_count_end_index]
        print(f'Found {occurrences_count} occurrences!')



        # LOOPING THROUGH EACH OCCURRENCE
        while True:


            
            # PARSING START INDEX FROM OCCURRENCE
            item_start_reference = '<tr class="resultado">'
            item_start_index = main_source.find(item_start_reference, item_start_index)



            if item_start_index == -1:
                break



            # PARSING END INDEX FROM OCCURRENCE
            item_end_reference = '</table>'
            item_end_index = main_source.find(item_end_reference, item_start_index)



            # SANITY CHECKS
            if item_end_index == -1:
                break
                # raise Exception(f'ERROR: No item_end_index({item_end_index}) found!')
            if item_start_index > item_end_index:
                raise Exception(f'ERROR: item_start_index({item_start_index}) GREATER THAN item_end_index({item_end_index})!')



            # UPDATING INDEX FOR NEXT ITERATION
            value_index = item_start_index



            # LOOPING THROUGH EACH VALUE FROM OCCURRENCE
            while True:



                # PARSING INDEXES FROM LIST
                list_column_start_reference = '<td class="col2"><b>'
                list_column_start_index = main_source.find(list_column_start_reference, value_index)
                list_column_end_reference = ':'
                list_column_end_index = main_source.find(list_column_end_reference, list_column_start_index)



                if list_column_start_index > item_end_index:
                    break

                

                # SANITY CHECKS
                if list_column_start_index == -1 or list_column_end_index == -1:
                    break
                    # raise Exception(f'ERROR: list_column_start_index({list_column_start_index}) or list_column_end_index({list_column_end_index}) not found!')
                if list_column_start_index > list_column_end_index:
                    raise Exception(f'ERROR: list_column_start_index({list_column_start_index}) is GREATER THAN list_column_end_index({list_column_end_index})!')



                # PARSING INDEXES FROM LIST
                list_value_start_reference = '<td class="col3">'
                list_value_start_index = main_source.find(list_value_start_reference, list_column_end_index)
                list_value_end_reference = '</td>'
                list_value_end_index = main_source.find(list_value_end_reference, list_value_start_index)   



                # SANITY CHECKS
                if list_value_start_index == -1 or list_value_end_index == -1:
                    raise Exception(f'ERROR: list_value_start_index({list_value_start_index}) or list_value_end_index({list_value_end_index}) not found!')
                if list_value_start_index > list_value_end_index:
                    raise Exception(f'ERROR: list_value_start_index({list_value_start_index}) is GREATER THAN list_value_end_index({list_value_end_index})!')



                # FETCHING COLUMN FROM LIST
                list_column_start_index += len(list_column_start_reference)
                list_column = main_source[list_column_start_index: list_column_end_index]



                # FETCHING VALUE FROM LIST
                list_value_start_index += len(list_value_start_reference)
                list_value = main_source[list_value_start_index: list_value_end_index]



                # print("-->  LIST  ", list_column, (list_value[:75] + '..') if len(list_value) > 75 else list_value, flush=True)
                value_index = list_value_start_index



                # TODO: SKIPPING Tipo Avulso DUE TO PDF FORMAT.
                if list_column == 'Tipo' and list_value == 'Avulso':
                    print(f'Tipo: Avulso. Skipping...')
                    break 



                # ADDING COLUMN AND VALUE TO MAIN DFS
                doc.attrs[list_column] = list_value



                if list_column == 'Título':
                    # FETCHING LIST LINK
                    link_start_reference = '<a href="'
                    link_end_reference = '">'
                    link_start_index = list_value.find(link_start_reference) + len(link_start_reference)
                    link_end_index = list_value.find(link_end_reference, link_start_index)
                    link = list_value[link_start_index:link_end_index]

                    new_list_value_start_reference = '">'
                    new_list_value_end_reference = '</a> <span'
                    new_list_value_start_index = list_value.find(new_list_value_start_reference) + len(new_list_value_start_reference)
                    new_list_value_end_index = list_value.find(new_list_value_end_reference, new_list_value_start_index)
                    new_list_value = list_value[new_list_value_start_index:new_list_value_end_index]
                    list_value = new_list_value



                    # PREPARING URL AND REQUEST FOR EACH OCCURRENCE
                    url = f'https://www6g.senado.gov.br/apem/{link}'
                    page_response = make_request(url)
                    page_source = page_response.text
                    


                    end_reference = '</div>'



                    # PARSING INITIAL INDEX FOR ALL COLUMNS
                    start_params_domain_reference = '<fieldset'
                    index = page_source.find(start_params_domain_reference)
                    finish_index = None



                    # LOOPING THOROUGH ITEMS IN LINK
                    while True:



                        # PARSING INITIAL INDEX FOR EACH COLUMN
                        column_start_reference = '<div class="result_col1">'
                        column_start_index = page_source.find(column_start_reference, index)



                        # CHECKING END OF OCCURRENCE PAGE
                        if column_start_index == -1:
                            break



                        # PARSING FINAL INDEX FOR EACH COLUMN
                        finish_reference = '<br class="clear" />'
                        finish_index = page_source.find(finish_reference, column_start_index)



                        # SANITY CHECKS
                        if finish_index == -1:
                            raise Exception(f'ERROR: No finish_reference({finish_reference}) found!')
                        if column_start_index > finish_index:
                            raise Exception(f'ERROR: column_start_index({column_start_index}) GREATER THAN finish_index({finish_index})!')



                        # PARSING POSSIBLE VALUE
                        value_start_opt1_reference = '<div class="result_col2">'
                        value_start_opt1_index = page_source.find(value_start_opt1_reference, column_start_index)
                        value_start_opt2_reference = '<div class="texto_pre">'
                        value_start_opt2_index = page_source.find(value_start_opt2_reference, column_start_index)
                        if value_start_opt1_index != -1 and value_start_opt2_index != -1:
                            if value_start_opt1_index < value_start_opt2_index:
                                value_start_index = value_start_opt1_index + len(value_start_opt1_reference)
                            else:
                                value_start_index = value_start_opt2_index + len(value_start_opt2_reference)
                        elif value_start_opt1_index != -1:
                            value_start_index = value_start_opt1_index + len(value_start_opt1_reference)
                        elif value_start_opt2_index != -1:
                            value_start_index = value_start_opt2_index + len(value_start_opt2_reference)
                        else:
                            raise Exception(f'ERROR: No {value_start_opt1_index} OR {value_start_opt1_index} found!')



                        # SANITY CHECKS
                        if value_start_index < column_start_index:
                            raise Exception(f'ERROR: value_start_index({value_start_index}) LOWER THAN column_start_index({column_start_index})')
                        if value_start_index > finish_index:
                            raise Exception(f'ERROR: value_start_index({value_start_index}) GREATER THAN finish_index({finish_index}.{page_source} ////// {page_source[finish_index:value_start_index]})')



                        # FETCHING COLUMN
                        column_start_index += len(column_start_reference)
                        column_end_index = page_source.find(end_reference, column_start_index)
                        column = page_source[column_start_index:column_end_index]



                        # FETCHING VALUE
                        value_end_index = page_source.find(end_reference, value_start_index)
                        value = page_source[value_start_index:value_end_index]


                        
                        # ADDING COLUMN AND VALUE TO MAIN DFS
                        doc.attrs[column] = value



                        # UPDATING INDEX FOR NEXT LOOP
                        index = finish_index

                        # print("-->  OCCURRENCE  ", column, (value[:75] + '..') if len(value) > 75 else value, flush=True)



            # SLEEPING A FEW SECONDS TO SIMULATE HUMAN NAVIGATION
            doc.eval()
            sleep()
            item_start_index = list_value_start_index
        


        print('###################', flush=True)



        # CHECKING IF CRAWLER HAS REACHED AN END
        if item_start_index == -1:
            break


        
        # INCREMENTING FOR NEXT PAGE OF OCCURRENCES
        page += 1
        sleep()

    doc.export(keyword)


if __name__ == '__main__':
    main()