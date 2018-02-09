import os
from reportlab.lib.pagesizes import A4, landscape
from PIL import Image, ImageFont, ImageDraw
from urllib.parse import urljoin
import time
import sys
import os
from PyPDF2 import PdfFileWriter, PdfFileReader
from .tool import upload_file, bucket_domain

page_size1 = (842, 595)
start_position = (87.5, 87.5)
font_type = 'tools/microsoft_yahei.ttf'
font_type_b = 'tools/microsoft_yahei_b.ttf'
page_size2 = (2105, 1487)
page_size3 = (1754, 1240)
page_size4 = (3508, 2479)
static_host = 'http://city.king:8080'

def draw_background(page_size):
    im = Image.new("RGB", (page_size[1], page_size[0]), (255, 255, 255))
    return im

def word_to_image(text, fone_type_file, font_size, im, position): 
    datas = text.split('\n')
    
    data = ''
    if not datas:
        datas = [text]
    for d in datas:
        if not d:
            d = ' '
        elif len(d) > 31:
            d1 = d[:30] + '\n'
            d2 = d[30:]
            d = d1 + ' \n'+ d2
        data += (d +'\n')
        data += ' \n'
        
    data = data[:-1]
    
    dr = ImageDraw.Draw(im)
    font = ImageFont.truetype(fone_type_file, font_size)
     
    dr.text(position, data, font=font, fill="#000000", spacing=0, align='left')
    #dr.line([10+2*14,5+15,10+5*14,5+15],fill = 10)
    #dr.text((10+5*14, 5), data2, font=font, fill='#000000')
     
#    im.show()
    im.save("t.png")
    return im, len(datas)
def roll(image, delta):
    "Roll an image sideways"

    xsize, ysize = image.size

    delta = delta % xsize
    if delta == 0: return image

    part1 = image.crop((0, 0, delta, ysize))
    part2 = image.crop((delta, 0, xsize, ysize))
    part1.load()
    part2.load()
    image.paste(part2, (0, 0, xsize-delta, ysize))
    image.paste(part1, (xsize-delta, 0, xsize, ysize))

    return image

def draw_tradecontractfirst_page(contract):
    font_size = 14
    lines = 0
    image = Image.open('static/jpg/trade_contract/trade_contract_1.jpg')
    image, line = word_to_image('甲方：'+contract.first_party, font_type_b, 28, image, (194,229))
    image, line = word_to_image('联系电话：' + contract.phone, font_type_b, 28, image, (194,294))
    image, line = word_to_image('联系地址：' +contract.address, font_type_b, 28, image, (194,358))
    image, line = word_to_image('交易宝服务应用场景：' + contract.application_scene, font_type_b, 28, image, (194,552-28))
    pdfname = '交易宝服务协议(最新)_%s_1.pdf' % contract.first_party
    image.save(pdfname)
    imgname = '交易宝服务协议(最新)_%s_1.jpg' % contract.first_party
    image.save(imgname)
    return pdfname, imgname 

def draw_tradecontractlast_page(contract):
    font_size = 14
    lines = 0
    image = Image.open('static/jpg/trade_contract/trade_contract_3_1.jpg')
    print(image.size)
    image, line = word_to_image('甲方：'+contract.first_party, font_type, 28, image, (94,358))
    image, line = word_to_image('日期：' + contract.date1, font_type, 28, image, (94,424))
    image, line = word_to_image('日期：' +contract.date2, font_type, 28, image, (94,620))
    image, line = word_to_image('使用本服务的交易宝账户及编号：' + contract.trade_accounts, font_type_b, 28, image, (190,824))
    pdfname = '交易宝服务协议_%s_3_1.pdf' % contract.first_party
    image.save(pdfname)
    imgname = '交易宝服务协议_%s_3_1.jpg' % contract.first_party
    image.save(imgname)
    return pdfname, imgname 

def draw_FinancingContract_second(contract):
    font_size = 14
    lines = 0
    if contract.contract_type=='FinancingContractDay':
        image = Image.open('static/FinancingContract/day/img/2.jpg')
    elif contract.contract_type=='FinancingContractMonth1':
        image = Image.open('static/FinancingContract/month1/img/2.jpg')
    elif contract.contract_type=='FinancingContractMonth2':
        image = Image.open('static/FinancingContract/month2/img/2.jpg')
    else:
        print('无此合同类型')
        return None
    image, line = word_to_image('投资方（甲方）：'+contract.first_party, font_type, 28, image, (190,390-61))
    image, line = word_to_image('身份证号码：'+contract.ID_card, font_type, 28, image, (190,456-61))
    image, line = word_to_image('联系电话：' + contract.phone, font_type, 28, image, (190,522-61))
    image, line = word_to_image('住       址：' +contract.address, font_type, 28, image, (190,588-61))
    pdfname = '日日红理财合同_%s_2.pdf' % contract.first_party
    image.save(pdfname)
    imgname = '日日红理财合同_%s_2.jpg' % contract.first_party
    image.save(imgname)
#    image.show()
    return pdfname, imgname 

def draw_FinancingContract_third(contract):
    font_size = 14
    lines = 0
    if contract.contract_type=='FinancingContractDay':
        image = Image.open('static/FinancingContract/day/img/3.jpg')
    elif contract.contract_type=='FinancingContractMonth1':
        image = Image.open('static/FinancingContract/month1/img/3.jpg')
    elif contract.contract_type=='FinancingContractMonth2':
        image = Image.open('static/FinancingContract/month2/img/3.jpg')
    else:
        print('无此合同类型')
        return None

#    info2 = '        投资份数 %d 份；投资金额人民币（大写 %s 万元整（¥ %.2f 元）。' % (contract.copies, contract.money_upper, contract.money)
    image, line = word_to_image(str(contract.copies), font_type, 28, image, (330,746))
    image, line = word_to_image(str(contract.money_upper), font_type, 28, image, (816,746))
    image, line = word_to_image(str(int(contract.money)), font_type, 28, image, (240,812))
    start_date = time.strptime(contract.start_date, '%Y/%m/%d')
#    info4 = '第四条 起投日期%s年%s月%s日' % (start_date.tm_year, start_date.tm_mon, start_date.tm_mday)
    image, line = word_to_image(str(start_date.tm_year), font_type, 28, image, (502,946))
    image, line = word_to_image(str(start_date.tm_mon), font_type, 28, image, (610,946))
    image, line = word_to_image(str(start_date.tm_mday), font_type, 28, image, (710,946))
    pdfname = '日日红理财合同_%s_3.pdf' % contract.first_party
    image.save(pdfname)
    imgname = '日日红理财合同_%s_3.jpg' % contract.first_party
    image.save(imgname)
#    image.show()
    return pdfname, imgname 

def draw_FinancingContract_forth(contract):
    font_size = 14
    lines = 0
    if contract.contract_type=='FinancingContractDay':
        image = Image.open('static/FinancingContract/day/img/4.jpg')
    elif contract.contract_type=='FinancingContractMonth1':
        image = Image.open('static/FinancingContract/month1/img/4.jpg')
    elif contract.contract_type=='FinancingContractMonth2':
        image = Image.open('static/FinancingContract/month2/img/4.jpg')
    else:
        print('无此合同类型')
        return None

    if contract.contract_type=='FinancingContractDay':
        image, line = word_to_image('开户全称：' + contract.account_holder8, font_type, 28, image, (256,556))
        image, line = word_to_image('开  户  行：' + contract.account_bank8, font_type, 28, image, (256,617))
        image, line = word_to_image('账       号：' + contract.account8, font_type, 28, image, (256,678))
    else:
        image, line = word_to_image(contract.pay_method, font_type, 28, image, (910,358))
        image, line = word_to_image('开户全称：' + contract.account_holder8, font_type, 28, image, (256,615))
        image, line = word_to_image('开  户  行：' + contract.account_bank8, font_type, 28, image, (256,686))
        image, line = word_to_image('账       号：' + contract.account8, font_type, 28, image, (256,747))
   
    pdfname = '日日红理财合同_%s_4.pdf' % contract.first_party
    image.save(pdfname)
    imgname = '日日红理财合同_%s_4.jpg' % contract.first_party
    image.save(imgname)
#    image.show()
    return pdfname, imgname 

def draw_FinancingContract_fifth(contract):
    font_size = 14
    lines = 0
    if contract.contract_type=='FinancingContractDay':
        image = Image.open('static/FinancingContract/day/img/5.jpg')
    elif contract.contract_type=='FinancingContractMonth1':
        image = Image.open('static/FinancingContract/month1/img/5.jpg')
    elif contract.contract_type=='FinancingContractMonth2':
        image = Image.open('static/FinancingContract/month2/img/5.jpg')
    else:
        print('无此合同类型')
        return None
    if contract.contract_type=='FinancingContractDay':
        image, line = word_to_image('开户全称：' + contract.account_holder10, font_type, 28, image, (256,422))
        image, line = word_to_image('开  户  行：' + contract.account_bank10, font_type, 28, image, (256,483))
        image, line = word_to_image('账       号：' + contract.account10, font_type, 28, image, (256,543))
    else:
        image, line = word_to_image('开户全称：' + contract.account_holder10, font_type, 28, image, (256,552))
        image, line = word_to_image('开  户  行：' + contract.account_bank10, font_type, 28, image, (256,613))
        image, line = word_to_image('账       号：' + contract.account10, font_type, 28, image, (256,673))

    pdfname = '日日红理财合同_%s_5.pdf' % contract.first_party
    image.save(pdfname)
    imgname = '日日红理财合同_%s_5.jpg' % contract.first_party
    image.save(imgname)
#    image.show()
    return pdfname, imgname 

def draw_FinancingContract_eighth(contract):
    font_size = 14
    lines = 0
    if contract.contract_type=='FinancingContractDay':
        image = Image.open('static/FinancingContract/day/img/8.jpg')
    elif contract.contract_type=='FinancingContractMonth1':
        image = Image.open('static/FinancingContract/month1/img/8.jpg')
    elif contract.contract_type=='FinancingContractMonth2':
        image = Image.open('static/FinancingContract/month2/img/8.jpg')
    else:
        print('无此合同类型')
        return None

    if contract.contract_type=='FinancingContractDay': 
        image, line = word_to_image('投资方（甲方）：' + contract.first_party, font_type, 28, image, (189,754))
        create_date = time.strptime(contract.create_date, '%Y/%m/%d')
        info = '合同签订时间：%s 年 %s 月 %s 日' % (create_date.tm_year, create_date.tm_mon, create_date.tm_mday)
        image, line = word_to_image(info, font_type, 28, image, (189,1526))
    else:
        image, line = word_to_image(contract.first_party, font_type, 28, image, (189+241,754+58))
        create_date = time.strptime(contract.create_date, '%Y/%m/%d')
        info = '合同签订时间：%s 年 %s 月 %s 日' % (create_date.tm_year, create_date.tm_mon, create_date.tm_mday)
        image, line = word_to_image(info, font_type, 28, image, (189,1526))
       
   
    pdfname = '日日红理财合同_%s_8.pdf' % contract.first_party
    image.save(pdfname)
    imgname = '日日红理财合同_%s_8.jpg' % contract.first_party
    image.save(imgname)
#    image.show()
    return pdfname, imgname 

def make_FinancingContract(contract):
    second_pdf, second_img = draw_FinancingContract_second(contract)
    third_pdf, third_img = draw_FinancingContract_third(contract)
    forth_pdf, forth_img = draw_FinancingContract_forth(contract)
    fifth_pdf, fifth_img = draw_FinancingContract_fifth(contract)
    eighth_pdf, eighth_img = draw_FinancingContract_eighth(contract)

    if contract.contract_type=='FinancingContractDay':
        first_pdf = 'static/FinancingContract/day/pdf/1.pdf'
        pdf6_7 = 'static/FinancingContract/day/pdf/6_7.pdf'
        img1 = static_host + '/static/FinancingContract/day/img/1.jpg'
        img6 = static_host + '/static/FinancingContract/day/img/6.jpg'
        img7 = static_host + '/static/FinancingContract/day/img/7.jpg'
        name = '理财产品日日红合同_%s.pdf' % contract.first_party
    elif contract.contract_type=='FinancingContractMonth1':
        first_pdf = 'static/FinancingContract/month1/pdf/1.pdf'
        pdf6_7 = 'static/FinancingContract/month1/pdf/6_7.pdf'
        img1 = static_host + '/static/FinancingContract/month1/img/1.jpg'
        img6 = static_host + '/static/FinancingContract/month1/img/6.jpg'
        img7 = static_host + '/static/FinancingContract/month1/img/7.jpg'
        name = '理财产品月月红套餐1合同_%s.pdf' % contract.first_party

    elif contract.contract_type=='FinancingContractMonth2':
        first_pdf = 'static/FinancingContract/month2/pdf/1.pdf'
        pdf6_7 = 'static/FinancingContract/month2/pdf/6_7.pdf'
        img1 = static_host + '/static/FinancingContract/month2/img/1.jpg'
        img6 = static_host + '/static/FinancingContract/month2/img/6.jpg'
        img7 = static_host + '/static/FinancingContract/month2/img/7.jpg'
        name = '理财产品月月红套餐2合同_%s.pdf' % contract.first_party
    else:
        print('无此合同类型')
        return None

    title = combine_pdf([first_pdf, second_pdf, third_pdf, forth_pdf, fifth_pdf, pdf6_7 ,eighth_pdf], name=name)

    os.remove(second_pdf)
    os.remove(third_pdf)
    os.remove(forth_pdf)
    os.remove(fifth_pdf)
    os.remove(eighth_pdf)

    img_url = []
    img_url.append(img1)
    url = upload_file(open(second_img, 'rb').read(), name=second_img)
    img_url.append(urljoin(bucket_domain, url))
    url = upload_file(open(third_img, 'rb').read(), name=third_img)
    img_url.append(urljoin(bucket_domain, url))
    url = upload_file(open(forth_img, 'rb').read(), name=forth_img)
    img_url.append(urljoin(bucket_domain, url))
    url = upload_file(open(fifth_img, 'rb').read(), name=fifth_img)
    img_url.append(urljoin(bucket_domain, url))
    img_url.append(img6)
    img_url.append(img7)
    url = upload_file(open(eighth_img, 'rb').read(), name=eighth_img)
    img_url.append(urljoin(bucket_domain, url))
    
    document_url = upload_file(open(title, 'rb').read(), name=title)
    document_url = urljoin(bucket_domain, document_url)
    document_size = len(open(title, 'rb').read())
    document_type = 'FinancingContract'
    document_title = title.split('.')[0]
    os.remove(second_img)
    os.remove(third_img)
    os.remove(forth_img)
    os.remove(fifth_img)
    os.remove(eighth_img)
    os.remove(title)
    data = dict(
           img_url=img_url,
           document_url=document_url,
           document_size=document_size,
           document_type=document_type,
           document_title=document_title
            )

    print(data)
    return data





def make_trade_contract(contract):
    first_pdf, first_img = draw_tradecontractfirst_page(contract)
    last_pdf, last_img = draw_tradecontractlast_page(contract)
    second_party = 'static/pdf/trade_contract/trade_contract_2.pdf'
    end_party = 'static/pdf/trade_contract/trade_contract_3_2.pdf'
    name = '交易宝服务协议_%s.pdf' % contract.first_party
    title = combine_pdf([first_pdf, second_party, last_pdf, end_party], name=name)
    os.remove(first_pdf)
    os.remove(last_pdf)
    img_url = []
    url = upload_file(open(first_img, 'rb').read(), name=first_img)
    img_url.append(urljoin(bucket_domain, url))
    url = upload_file(open(last_img, 'rb').read(), name=last_img)
    img_url.append(urljoin(bucket_domain, url))
    document_url = upload_file(open(title, 'rb').read(), name=title)
    document_url = urljoin(bucket_domain, document_url)
    document_size = len(open(title, 'rb').read())
    document_type = 'trade_contract'
    document_title = title.split('.')[0]
    os.remove(first_img)
    os.remove(last_img)
    os.remove(title)
    return dict(
           img_url=img_url,
           document_url=document_url,
           document_size=document_size,
           document_type=document_type,
           document_title=document_title
            )

def make_contract(contract, contract_type):
    if contract_type == 'trade_contract':
        return make_trade_contract(contract)
    else: 
        return make_FinancingContract(contract)

def combine_pdf(files, name):
    output=PdfFileWriter()
    outputPages=0
    
    for filename in files:
        # 读取源pdf文件
        input=PdfFileReader(open(filename,"rb"))
        
        # 如果pdf文件已经加密，必须首先解密才能使用pyPdf
        if input.isEncrypted == True:
            input.decrypt("map")
        
        # 获得源pdf文件中页面总数
        pageCount=input.getNumPages()
        outputPages+=pageCount
    # 分别将page添加到输出output中
        for iPage in range(0,pageCount):
            output.addPage(input.getPage(iPage))    
    # 最后写pdf文件
    i = 1
    while os.path.exists(name):   
        names = name.split('.')
        name = names[0] + str(i) + '.pdf'
        i += 1
    outputStream=open(name,"wb")
    output.write(outputStream)
    outputStream.close()
    return name 

def combine():
    combine_pdf(['交易宝服务协议(最新)_1.pdf', '交易宝服务协议(最新)_2.pdf', '交易宝服务协议(最新)_3_1.pdf', '交易宝服务协议(最新)_3_2.pdf'])


if __name__ == "__main__":
    pass

