<?xml version="1.0" encoding="utf-8"?>

<!-- ======================================================== -->
<!-- File    : PROTEUS_traceability_matrix.xsl                -->
<!-- Content : PROTEUS XSLT for subjects at US - section      -->
<!-- Author  : José María Delgado Sánchez                     -->
<!-- Date    : 2023/06/09                                     -->
<!-- Version : 1.0                                            -->
<!-- ======================================================== -->

<!-- ======================================================== -->
<!-- exclude-result-prefixes="proteus" must be set in all     -->
<!-- files to avoid xmlsn:proteus="." to appear in HTML tags. -->
<!-- ======================================================== -->

<xsl:stylesheet version="1.0"
    xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
    xmlns:proteus="http://proteus.us.es"
    xmlns:proteus-utils="http://proteus.us.es/utils"
    exclude-result-prefixes="proteus proteus-utils"
>

    <xsl:template match="object[@classes='traceability-matrix']">
        <div id="{@id}" class="traceability_matrix">

            <!-- Extract row and column classes -->
            <xsl:variable name="col-classes">
                <xsl:apply-templates select="properties/classListProperty[@name='col-classes']/class"/>
            </xsl:variable>

            <xsl:variable name="row-classes">
                <xsl:apply-templates select="properties/classListProperty[@name='row-classes']/class"/>
            </xsl:variable>

            <!-- Get column and row items -->
            <xsl:variable name="col-items" select="proteus-utils:get_objects_from_classes($col-classes)"/>
            <xsl:variable name="row-items" select="proteus-utils:get_objects_from_classes($row-classes)"/>
            
            <!-- If the are no col or row classes, warns the user and do not create the matrix -->
            <xsl:choose>
                <xsl:when test="count($col-items) = 0 or count($row-items) = 0">
                    <h1>WARNING: Traceability matrix is not properly configured. Please, check the configuration.</h1>
                </xsl:when>
                <xsl:otherwise>
                    <xsl:call-template name="create-traceability-matrix">
                        <xsl:with-param name="col-items" select="$col-items"/>
                        <xsl:with-param name="row-items" select="$row-items"/>
                    </xsl:call-template>
                </xsl:otherwise>
            </xsl:choose>
        </div>
    </xsl:template>


    <!-- This template helps creating a list of classes separated by spaces.-->
    <!-- Proteus classes cannot contain spaces so this is supposed to be a  -->
    <!-- safe separator.                                                    -->
    <xsl:template match="class">
        <xsl:value-of select="normalize-space(.)"/>
        <xsl:text> </xsl:text>
    </xsl:template>


    <!-- Traceability Matrix templates ==================================== -->

    <!-- Table tag -->
    <xsl:template name="create-traceability-matrix">
        <xsl:param name="col-items"/>
        <xsl:param name="row-items"/>

        <table class="traceability_matrix remus_table">
            <thead>
                <xsl:call-template name="create-traceability-matrix-header">
                    <xsl:with-param name="col-items" select="$col-items"/>
                </xsl:call-template>
            </thead>
            <tbody>
                <xsl:for-each select="$row-items">
                    <tr>
                        <xsl:call-template name="create-traceability-matrix-row">
                            <xsl:with-param name="col-items" select="$col-items"/>
                        </xsl:call-template>
                    </tr>
                </xsl:for-each>
            </tbody>
        </table>
    </xsl:template>

    <!-- Table header -->
    <xsl:template name="create-traceability-matrix-header">
        <xsl:param name="col-items"/>
            <th class="matrix_oid">
                <img src="templates:///default/resources/images/traceabilityMatrix.png"/>
                <xsl:text> </xsl:text>
                <!-- <span class="matriz_oid"><xsl:value-of select="@id"/></span> -->
                <span class="matriz_oid">prueba</span>
            </th>

            <xsl:for-each select="$col-items">
                <xsl:variable name="label" select="label"/>

                <th class="matrix_column">
                    <a href="#{@id}" onclick="selectAndNavigate(`{@id}`, event)" title="{$label}">
                        <xsl:value-of select="$label"/>
                    </a>
                </th>
            </xsl:for-each>
    </xsl:template>

    <!-- Traceability row -->
    <xsl:template name="create-traceability-matrix-row">
        <xsl:param name="col-items"/>

        <xsl:variable name="label" select="label"/>
        <xsl:variable name="row-item-id" select="@id"/>

        <th>
            <a href="#{@id}" onclick="selectAndNavigate(`{@id}`, event)" title="{$label}">
                <xsl:value-of select="$label"/>
            </a>
        </th>

        <xsl:for-each select="$col-items">
            <td>
                <xsl:variable name="has-dependency" select="proteus-utils:check_dependency($row-item-id, @id)"/>
                <xsl:choose>
                    <xsl:when test="$has-dependency = 'True'">
                        <xsl:attribute name="class">trace</xsl:attribute>
                        <img class="trace" src="templates:///default/resources/images/traceabilityMatrixArrow.png"/>
                    </xsl:when>
                    <xsl:otherwise>
                        <xsl:text>-</xsl:text>
                    </xsl:otherwise>
                </xsl:choose>
            </td>
        </xsl:for-each>

    </xsl:template>


</xsl:stylesheet>